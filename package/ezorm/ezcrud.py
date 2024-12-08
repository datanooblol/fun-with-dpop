from package.ezorm.variables import EzORM
from typing import List, Type, Tuple, Dict, Union
from package.ezorm.utils import remove_escape_characters
import json
from package.ezorm.configuration import settings
import pandas as pd
from package.ezorm.validation import isinstance_ezorm

def clean_and_execute(query:str, data:list=[])->pd.DataFrame:
    query = remove_escape_characters(query)
    data = remove_escape_characters(json.dumps(data))
    data = json.loads(data)
    return settings.engine(query+";", data)

def get_table_and_schemas(model:Type[EzORM])->Tuple[str, Dict[str, Union[str, int, bool]]]:
    isinstance_ezorm(model)
    table = model.__table__
    schemas = model.model_dump()
    return table, schemas

def get_condition_and_data(schemas:dict)->Tuple[List[str], List[Union[str, int, bool]]]:
    condition = []
    data = []
    for field, value in schemas.items():
        if value is not None:
            condition.append(f"{field}=?")
            data.append(value)
    return condition, data

import duckdb

class DatabaseConnectionManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        # Open the connection
        print(f"Opening database connection to {self.db_path}")
        self.connection = duckdb.connect(self.db_path)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        # Close the connection
        if self.connection:
            print("Closing database connection")
            self.connection.close()
        return False  # Propagate exceptions, do not suppress


class Engine:
    def connect(self): return
    def execute(self): return
    
class EzCrud:
    def __init__(self, engine:Engine, database:str):
        self.engine:Engine = engine
        self.database = database

    def execute(self, query, data):
        with self.engine.connect(self.database) as con:
            return con.execute(query, data).df()

    def Create(self, model:Type[EzORM])->pd.DataFrame:
        table, schemas = get_table_and_schemas(model)
        query = f"INSERT INTO {table} VALUES ({', '.join(['?' for i in range(len(schemas))])})"
        data = [value for value in schemas.values()]
        return self.execute(query, data)

    def Read(self, model:Type[EzORM])->pd.DataFrame:
        table, schemas = get_table_and_schemas(model)
        where, data = get_condition_and_data(schemas)
        query = f"SELECT * FROM {table}"
        if len(where)>0:
            where = " AND ".join(where)
            query = f"{query} WHERE {where}"
        return self.execute(query, data)

    def Update(self, existing:Type[EzORM], new:Type[EzORM])->pd.DataFrame:
        e_table, e_schemas = get_table_and_schemas(existing)
        n_table, n_schemas = get_table_and_schemas(new)
        if e_table != n_table:
            raise ValueError("table not matched")
        e_where, e_data = get_condition_and_data(e_schemas)
        e_where = " AND ".join(e_where)
        n_set, n_data = get_condition_and_data(n_schemas)
        n_set = ", ".join(n_set)
        query = f"UPDATE {n_table} SET {n_set} WHERE {e_where}"
        data = n_data + e_data
        return self.execute(query, data)

    def Delete(self, model:Type[EzORM])->pd.DataFrame:
        table, schemas = get_table_and_schemas(model)
        where, data = get_condition_and_data(schemas)
        where = " AND ".join(where)
        query = f"DELETE FROM {table} WHERE {where}"
        return self.execute(query, data)