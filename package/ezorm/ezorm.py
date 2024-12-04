# from typing import List, Type
# from package.ezorm.base import BaseORM
# from package.ezorm.utils import duck_connection
# from package.ezorm import DATABASE

# class Column:
#     def __init__(self, name: str, column_type: str, nullable: bool = True, primary_key: bool = False):
#         self.name = name
#         self.column_type = column_type
#         self.nullable = nullable
#         self.primary_key = primary_key

#     def __repr__(self):
#         return f"{self.name} ({self.column_type})"

# class EzDuckORM(BaseORM):

#     @classmethod
#     def create_tables(cls, tables: List[Type["EzDuckORM"]]):
#         """Creates tables if they don't exist and updates the schema if necessary."""
#         if not isinstance(tables, list):
#             raise ValueError("tables must be a list")

#         for table in tables:
#             if not issubclass(table, EzDuckORM):
#                 raise ValueError(f"Each item must be a subclass of EzDuckORM, found: {table.__name__}")

#             if cls.table_not_exist(table):
#                 query = table.create_tbl_query()
#                 cls.execute(query=query, data=[])
#                 print(f"Creating table for model: {table.__name__}")
#             else:
#                 print(f"Table for model: {table.__name__} already exists")
#         print("All tables processed successfully")

#     @classmethod
#     def table_not_exist(cls, table: Type["EzDuckORM"]) -> bool:
#         # """Checks if the table exists in the database."""
#         # query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table.table()}'"
#         # with duck_connection(DATABASE) as con:
#         #     result = con.execute(query).fetchone()
#         #     return result[0] == 0
#         return True
        
#     @classmethod
#     def delete_tables(cls, tables: List[Type["EzDuckORM"]]):
#         if not isinstance(tables, list):
#             raise ValueError("tables must be a list")

#         for table in tables:
#             if not issubclass(table, EzDuckORM):
#                 raise ValueError(f"Each item must be a subclass of EzDuckORM, found: {table.__name__}")
            
#             query = f"DROP TABLE IF EXISTS {table.table()}"
#             cls.execute(query)
#             print(f"Deleting table for model: {table.__name__}")

#         print("All tables deleted successfully")

#     @classmethod
#     def test_table(cls):
#         if cls.__table__ is None:
#             return cls.__name__.lower()
#         return cls.__table__.lower()

