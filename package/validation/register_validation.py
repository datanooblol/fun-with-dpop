import uuid
from fastapi import Body, Request, HTTPException
from package.database_management.data_models import RegisterFormat, UserModel
from package.ezorm.crud import Create, Read

def validate_register_request(request: Request, user:RegisterFormat=Body(...))->RegisterFormat:
    # user = RegisterFormat(**request.body)
    if Read(UserModel(username=user.username, password=user.password)).shape[0]>0:
        raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")
    return user