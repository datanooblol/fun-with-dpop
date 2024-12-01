from pydantic import BaseModel
from typing import List, Type
from package.ezorm.utils import duck_connection

DATABASE = "./db/ezorm.db"

class BaseORM(BaseModel):
    __table__: str  = None# Placeholder for table name

class EzORM(BaseORM):

    @classmethod
    def create_tables(cls, tables: List[Type["EzORM"]]):
        """Creates tables if they don't exist and updates the schema if necessary."""
        # Validate that the input `tables` is a list of EzORM subclasses
        if not isinstance(tables, list):
            raise ValueError("tables must be a list")
        
        for table in tables:
            # Ensure that each item in the list is a subclass of EzORM
            if not issubclass(table, EzORM):
                raise ValueError(f"Each item must be a subclass of EzORM, found: {table.__name__}")
            with duck_connection(DATABASE) as con:
                if table.__table__ is None:
                    table_name = table.__name__.lower()
                else:
                    table_name = table.__table__
                query=f"""CREATE TABLE IF NOT EXISTS {table_name} (id TEXT, client_id TEXT);"""
                # data = [table.__table__]
                con.execute(query)
            print(f"Creating or updating table for model: {table.__name__}")
            # Here, you'd add logic for creating or updating the schema of the table
            # For example, checking if the table exists and updating its schema if necessary

        print("All tables processed successfully")


