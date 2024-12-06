# from pydantic import BaseModel, Field, field_validator
# from typing import List, Dict, Any, Optional, Annotated, get_args, Union, Callable, ClassVar
# from fastapi import HTTPException
# import uuid
# from package.database_management.utils import DB
# from package.configurations import db_path
# from package.ezorm.variables import EzORM

# class BaseToken(EzORM):
#     def create(self):
#         return self.table
    
#     def read(self):
#         return self.table

#     def update(self):
#         return self.table
    
#     def delete(self):
#         return self.table

# class DPoPModel(BaseToken):
#     jti:str = Field(description="", default_factory=lambda: str(uuid.uuid4()))

#     def create(self, db:DB):
#         query = f"""INSERT INTO {self.table} VALUES (?)"""
#         data = [self.jti]
#         return db.execute(query, data)


# class AccessTokenModel(DPoPModel):
#     access_token:Optional[str] = Field(description="", default=None)
#     client_id:Optional[str] = Field(description="", default=None)
#     exp:Optional[int] = Field(description="", default=None)
#     active:Optional[bool] = Field(description="", default=True)
#     remark:Optional[str] = Field(description="", default="")

#     def create(self, db:DB):
#         query = f"""INSERT INTO {self.table} VALUES (?, ?, ?, ?, ?, ?)"""
#         data = [self.jti, self.access_token, self.client_id, self.exp, self.active, self.remark]
#         return db.execute(query, data)

# class RefreshTokenModel(AccessTokenModel):
#     refresh_token:Optional[str] = Field(description="", default=None)

#     def create(self, db:DB):
#         print(self.active)
#         query = f"""INSERT INTO {self.table} VALUES (?, ?, ?, ?, ?, ?, ?)"""
#         data = [self.jti, self.access_token, self.client_id, self.exp, self.active, self.remark, self.refresh_token]
#         return db.execute(query, data)