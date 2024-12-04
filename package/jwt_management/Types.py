from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Annotated, get_args, Union
from fastapi import HTTPException
import time
import json
import base64
import hashlib
import uuid
from jose import jwt

class Base(BaseModel):
    alg:str = Field(description="", default="RS256")
    jti:str = Field(description="", default_factory=lambda: str(uuid.uuid4()))
    iat:int = Field(description="", default_factory=lambda: int(time.time()))
    exp:Optional[Union[int, None]] = Field(description="", default=None)

    @field_validator('exp', mode="before")
    def validate_exp(cls, value:Union[int, None])->int:
        iat = cls.iat
        if value is None:
            return iat + 30
        return iat + value

class BaseJWK(Base):
    e:str = Field(description="")
    kty:str = Field(description="")
    n:str = Field(description="")
    
    @field_validator('kty', mode="before")
    def validate_kty(cls, value:str)->str:
        available_algorithm = ["RSA"]
        if value not in available_algorithm:
            raise HTTPException(status_code=400, detail=f"kty must be in {available_algorithm}, instead '{value}")
        return value

class BaseHeaders(Base):
    typ:str = Field(description="", default="dpop+jwt")
    jwk:BaseJWK = Field(description="") # check later

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

class BasePayload(Base):
    client_id:str = Field(description="")
    
class ClientPayload(BasePayload):
    htm:str = Field(description="")
    htu:str = Field(description="")
    
    @field_validator('htm', mode="before")
    def validate_htm(cls, value:str)->str:
        value = value.upper()
        availables = ["GET", "POST"]
        if value not in availables:
            raise HTTPException(status_code=400, detail=f"htm must be in {availables}, instead '{value}'")
        return value
    
class ServerPayload(BasePayload):
    cnf:Optional[Union[Dict[str, str], None]] = Field(description="", default=None)
    
    @field_validator('cnf', mode="before")
    def validate_cnf(cls, value:Union[Dict[str, str], None])->str:
        if value is not None:
            if "jkt" not in cls:
                raise HTTPException(status_code=400, detail=f"jkt not found, jkt must be 
                in cnf")
        
    def generate_token(self, key:bytes)->str:
        self.jti, self.iat, self.exp, self.client_id, self.cnf
        claims = {
            "iat": self.iat,
            "exp": self.exp,
            "jti": self.jti,
            "client_id": self.client_id,
        }
        if self.cnf is not None:
            claims.update({"cnf": self.cnf})
        return jwt.encode(claims=claims, key=key, algorithm=self.alg)

class JWK2Thumbprint(BaseJWK):
    def to_json(self)->str:
        return json.dumps(self.model_dump(), separators=(',',':'), sort_keys=True)
    
    def to_sha256_hash(self)->bytes:
        canonical_jwk = self.to_json()
        return hashlib.sha256(canonical_jwk.encode("utf-8")).digest()

    def to_base64url(self)->str:
        sha256_hash = self.to_sha256_hash()
        return base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')

    def to_thumbprint(self)->Dict[str, str]:
        return {"jkt": self.to_base64url()}