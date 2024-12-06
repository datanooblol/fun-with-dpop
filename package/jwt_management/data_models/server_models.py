from pydantic import BaseModel, Field
from typing import Optional
from jose import jwt
from package.jwt_management.data_models.base_models import JWK
from fastapi import HTTPException

ALGORITHM = "RS256"

class JKT(BaseModel):
    jkt:str = Field(description="")

    @classmethod
    def from_key(cls, key:bytes):
        return cls(jkt=JWK.from_key(key).to_thumbprint())

# clear
# class CNF(BaseModel):
#     cnf:JKT = Field(description="")

#     @classmethod
#     def from_key(cls, key:bytes):
#         return cls(
#             cnf=JKT(
#                 jkt=JWK.from_key(key).to_thumbprint()
#             ).model_dump()
#         )
#clear
class ServerSignature(BaseModel):
    jti:str = Field(description="")
    iat:int = Field(description="")
    exp:int = Field(description="")
    client_id:str = Field(description="")
    cnf:JKT = Field(description="", default=None)
    
    def sign(self, key:bytes)->str:
        claims = {}
        for name, value in self.model_dump().items():
            if (value is not None):
                claims[name] = value
        return jwt.encode(claims=claims, key=key, algorithm=ALGORITHM)

    @classmethod
    def verify_signature(cls, signature:str, key:bytes):
        try:
            decoded = jwt.decode(
                token=signature,
                key=key,
                algorithms=ALGORITHM
            )
            return cls(**decoded)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unexpected error: {e}")