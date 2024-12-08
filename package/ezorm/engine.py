import duckdb
import pandas as pd
from package.ezorm.configuration import settings

def duck_engine(query:str, data:list, db_path:str=None)->pd.DataFrame:
    if db_path is None:
        db_path = settings.database
    with duckdb.connect(db_path) as con:
        return con.execute(query, data).df()