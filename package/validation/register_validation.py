import uuid
from fastapi import Body, Depends, Request, HTTPException
from package.database_management.data_models import RegisterFormat, UserModel
from package.ezorm.crud import Create, Read
from package.ezorm.ezcrud import EzCrud
from package.utils import get_db

# def validate_register_request(request: Request, user:RegisterFormat=Body(...))->RegisterFormat:
#     # user = RegisterFormat(**request.body)
#     if Read(UserModel(username=user.username, password=user.password)).shape[0]>0:
#         raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")
#     return user

def validate_register_request(user:RegisterFormat, db:EzCrud=Depends(get_db))->RegisterFormat:
    # user = RegisterFormat(**request.body)
    if db.Read(UserModel(username=user.username, password=user.password)).shape[0]>0:
        raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")
    return user