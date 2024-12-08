from fastapi import Depends, HTTPException
from package.database_management.data_models import RegisterFormat, UserModel
from package.ezorm.ezcrud import EzCrud
from package.utils import get_db

def validate_register_request(user:RegisterFormat, db:EzCrud=Depends(get_db))->RegisterFormat:
    if db.Read(UserModel(username=user.username, password=user.password)).shape[0]>0:
        raise HTTPException(status_code=400, detail=f"User '{user.username}' already exists")
    return user