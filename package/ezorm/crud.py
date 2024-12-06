from package.ezorm.variables import EzORM
from typing import List, Type, Tuple, Dict, Union
from package.ezorm.utils import remove_escape_characters
import json
from package.ezorm.configuration import settings
import pandas as pd
from package.ezorm.validation import isinstance_ezorm
from fastapi import HTTPException

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

def Create(model:Type[EzORM])->pd.DataFrame:
    table, schemas = get_table_and_schemas(model)
    if Read(model).shape[0]!=0:
        raise HTTPException(status_code=400, detail="Record already exists")
    query = f"INSERT INTO {table} VALUES ({', '.join(['?' for i in range(len(schemas))])})"
    data = [value for value in schemas.values()]
    return clean_and_execute(query, data)

def Read(model:Type[EzORM])->pd.DataFrame:
    table, schemas = get_table_and_schemas(model)
    where, data = get_condition_and_data(schemas)
    query = f"SELECT * FROM {table}"
    if len(where)>0:
        where = " AND ".join(where)
        query = f"{query} WHERE {where}"
    return clean_and_execute(query, data)

def Update(existing:Type[EzORM], new:Type[EzORM])->pd.DataFrame:
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
    return clean_and_execute(query, data)

def Delete(model:Type[EzORM])->pd.DataFrame:
    table, schemas = get_table_and_schemas(model)
    where, data = get_condition_and_data(schemas)
    where = " AND ".join(where)
    query = f"DELETE FROM {table} WHERE {where}"
    return clean_and_execute(query, data)