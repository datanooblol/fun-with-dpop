# import duckdb
# import os

# class DB:
#     def __init__(self, db_path:str):
#         self.db = duckdb.connect
#         self.directory = None
#         self.filename = None
#         self.db_path = self.__path_validation(db_path)

#     def __path_validation(self, db_path:str)->str:
#         extensions = ['db']
#         extension = db_path.split(".")[-1]
#         if not extension in extensions:
#             raise ValueError(f"File extension should be one of these: {extensions} but yours was {extension}")
#         self.directory = os.path.dirname(db_path)
#         self.filename = os.path.basename(db_path)
#         return db_path
    
#     def create_database(self, table:str, schemas:str):
#         if not os.path.exists(self.db_path):
#             os.makedirs(self.directory, exist_ok=True)
#         df = self.list_table()
#         if df.loc[df['name']==table].shape[0] == 0:
#             query = f"CREATE TABLE {table} {schemas}".strip().replace('"',"").replace("'", "")
#             self.db_context(query=query)
#             print(query)
    
#     def execute(self, query, data):
#         with self.db(self.db_path) as con:
#             con.execute(query, data)

#     def delete_database(self, ):
#         self.db(self.db_path).close()
#         os.remove(self.db_path)

#     def list_table(self, ):
#         with self.db(self.db_path) as con:
#             df = con.execute("""SHOW TABLES;""").df()
#         return df