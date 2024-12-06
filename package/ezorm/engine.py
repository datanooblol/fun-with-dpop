import duckdb
import pandas as pd

def duck_engine(query:str, data:list, db_path:str="./db/ezorm.db")->pd.DataFrame:
    with duckdb.connect(db_path) as con:
        return con.execute(query, data).df()