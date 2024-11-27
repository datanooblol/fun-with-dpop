import duckdb
import os
from typing import List
from fastapi import HTTPException
from pydantic import BaseModel

class BaseFormat(BaseModel):
    jti:str


class DPoPFormat(BaseFormat):
    pass

class TokenFormat(BaseFormat):
    token: str
    client_id:str
    exp: int
    active: bool
    remark: str

class BaseDuckDB:
    def __init__(self, db_path:str):
        self.db = duckdb.connect
        self.directory = None
        self.filename = None
        self.db_path = self.path_validation(db_path)

    def path_validation(self, db_path:str)->str:
        extensions = ['db']
        extension = db_path.split(".")[-1]
        if not extension in extensions:
            raise ValueError(f"File extension should be one of these: {extensions} but yours was {extension}")
        self.directory = os.path.dirname(db_path)
        self.filename = os.path.basename(db_path)
        return db_path
    
    def create_database(self, table:str, schemas:str):
        if not os.path.exists(self.db_path):
            os.makedirs(self.directory, exist_ok=True)
        df = self.list_table()
        if df.loc[df['name']==table].shape[0] == 0:
            query = f"CREATE TABLE {table} {schemas}".strip().replace('"',"").replace("'", "")
            self.db_context(query=query)
            print(query)

    def db_context(self, query):
        with self.db(self.db_path) as con:
            con.sql(query)

    def query(self, query):
        with self.db(self.db_path) as con:
            df = con.sql(query).df()
        return df
    
    def execute(self, query, data):
        with self.db(self.db_path) as con:
            con.execute(query, data)

    def add_data(self, table:str, data:List[TokenFormat | DPoPFormat]):
        with self.db(self.db_path) as con:
            con.executemany(
                f"INSERT INTO {table} VALUES {tuple(['?' for i in range(len(data[0]))])}".replace("'", ""),
                data
            )
        return self

    def delete_database(self, ):
        self.db(self.db_path).close()
        os.remove(self.db_path)

    def list_table(self, ):
        with self.db(self.db_path) as con:
            df = con.execute("""SHOW TABLES;""").df()
        return df
    
class DBManagement(BaseDuckDB):
    def __init__(self, db_path):
        super().__init__(db_path)

    def add_jti(self, table:str, jti:str, token:str=None, client_id:str=None, exp:int=None, active:bool=None, remark:str=None):
        data = []
        for d in [jti, token, client_id, exp, active, remark]:
            if d is not None:
                data.append(d)
        self.add_data(table, [data])

    def update_token(self, table:str, jti:str, client_id:str, token:str, exp:int):
        query = f"UPDATE {table} SET token = ?, exp = ? WHERE jti = ? AND client_id = ?;"
        data = (token, exp, jti, client_id)
        self.execute(query, data)

    def update_active(self, table:str, jti:str, client_id:str, active:bool=None):
        query = f"UPDATE {table} SET active = ? WHERE jti = ? AND client_id = ?;"
        data = (active, jti, client_id)
        self.execute(query, data)

    def delete_token(self, table:str, jti:str, client_id:str):
        query = f"DELETE {table} WHERE jti = ? AND client_id = ?;"
        data = (jti, client_id)
        self.execute(query, data)

    def add_token(self, table:str, jti:str, token:str, client_id:str, exp:int, active:bool, remark:str):
        self.add_jti(table=table, jti=jti, token=token, client_id=client_id, exp=exp, active=active, remark=remark)

    def disable_token(self, table, client_id):
        query = f"UPDATE {table} SET active = ?, remark = ? WHERE client_id=='{client_id}';"
        self.execute(query, [False, "disable"])

    def dpop_is_unique(self, table:str, jti:str):
        query = f"SELECT jti FROM {table} WHERE jti=='{jti}';"
        df = self.query(query)
        if df.shape[0]!=0:
            raise HTTPException(status_code=400, detail="DPoP jti already exists.")
        else:
            self.add_jti(table=table, jti=jti)

    def token_is_valid(self, table:str, jti:str, token:str, client_id:str, exp:int):
        query = f"SELECT * FROM {table} WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}' AND exp=={exp} AND active=={True};"
        df = self.query(query)
        if df.shape[0]!=1:
            query = f"UPDATE {table} SET active = ? WHERE jti = ? AND token = ? AND client_id = ?;"
            data = (False, jti, token, client_id)
            self.execute(query, data)
            raise HTTPException(status_code=400, detail="invalid access token")
        