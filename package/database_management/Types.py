from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Annotated, get_args, Union
from fastapi import HTTPException
from jose import jwt
import uuid
import time

class BaseToken(BaseModel):
    # algorithm:str = Field(description="", default="")
    # iat:str = Field(description="", default=int(time.time()))
    ...

class DPoPModel(BaseToken):
    jti:str = Field(description="", default_factory=lambda: str(uuid.uuid4()))

class AccessTokenModel(DPoPModel):
    access_token:Optional[str] = Field(description="", default=None)
    client_id:Optional[str] = Field(description="", default=None)
    exp:Optional[int] = Field(description="", default=None)
    active:Optional[bool] = Field(description="", default=True)
    remark:Optional[str] = Field(description="", default="")

    def create(self):
        return "createed already"
    
    def read(self):
        return "read already"

    def update(self):
        return "updated already"
    
    def delete(self):
        return "deleted already"

class RefreshTokenModel(AccessTokenModel):
    refresh_token:Optional[str] = Field(description="", default=None)