from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Annotated, get_args
from fastapi import HTTPException
import time
import json
import base64
import hashlib
import uuid

class BaseJWK(BaseModel):
    e:str = Field(description="")
    kty:str = Field(description="")
    n:str = Field(description="")
    
    @field_validator('kty', mode="before")
    def validate_kty(cls, value:str)->str:
        available_algorithm = ["RSA"]
        if value not in available_algorithm:
            raise HTTPException(status_code=400, detail=f"kty must be in {available_algorithm}, instead '{value}")
        return value

class BaseHeaders(BaseModel):
    typ:str = Field(description="", default="dpop+jwt")
    alg:str = Field(description="", default="RS256")
    jwk:BaseJWK = Field(description="")

    @field_validator('alg', mode="before")
    def validate_alg(cls, value:str)->str:
        available_algorithm = ["RS256"]
        if value not in available_algorithm:
            raise HTTPException(status_code=400, detail=f"alg must be in {available_algorithm}, instead '{value}")
        return value
    
    @field_validator('typ', mode="before")
    def validate_typ(cls, value:str)->str:
        availables = ["dpop+jwt"]
        if value not in availables:
            raise HTTPException(status_code=400, detail=f"typ must be in {availables}, instead '{value}")
        return value

    def to_dict(self):
        return self.model_dump()

class ClientHeaders(BaseHeaders):
    ...

class BasePayload(BaseModel):
    htm:str = Field(description="")
    htu:str = Field(description="")
    iat:int = Field(description="", default=int(time.time()))
    exp:int = Field(description="")
    jti:str = Field(description="", default=str(uuid.uuid4()))

    @field_validator('htm', mode="before")
    def validate_htm(cls, value:str)->str:
        value = value.upper()
        availables = ["GET", "POST"]
        if value not in availables:
            raise HTTPException(status_code=400, detail=f"htm must be in {availables}, instead '{value}'")
        return value
    
class ClientPayload(BasePayload):
    client_id:str = Field(description="")

class JWK2Thumbprint(BaseJWK):
    def to_json(self):
        return json.dumps(self.model_dump(), separators=(',',':'), sort_keys=True)
    
    def to_sha256_hash(self):
        canonical_jwk = self.to_json()
        return hashlib.sha256(canonical_jwk.encode("utf-8")).digest()

    def to_base64url(self):
        sha256_hash = self.to_sha256_hash()
        return base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')

    def to_thumbprint(self):
        return self.to_base64url()