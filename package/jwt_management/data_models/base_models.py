from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Any, Optional, Union, get_args, Callable
from fastapi import HTTPException
from jose import jwt
from package.jwt_management.encode_decode import convert_key_to_jwk, convert_string_to_base64url, convert_jwk_to_public_key_pem
import json
import hashlib

ALGORITHM = "RS256"

#clear
class JWK(BaseModel):
    e:str = Field(description="")
    kty:str = Field(description="")
    n:str = Field(description="")

    @field_validator('kty', mode="before")
    def validate_kty(cls, value:str)->str:
        availables = ["RSA"]
        if value not in availables:
            raise HTTPException(status_code=400, detail=f"kty must be in {availables}, instead '{value}")
        return value
    
    @classmethod
    def from_key(cls, key:bytes):
        jwk_dict = convert_key_to_jwk(key)
        return cls(**jwk_dict)
    
    def to_thumbprint(self):
        model = self.model_dump()
        canonical_jwk = json.dumps(model, separators=(',', ':'), sort_keys=True)
        sha256_hash = hashlib.sha256(canonical_jwk.encode("utf-8")).digest()
        return convert_string_to_base64url(sha256_hash)
    
    def to_key(self):
        key = self.model_dump()
        return convert_jwk_to_public_key_pem(key)