from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException
from jose import jwt
from package.jwt_management.encode_decode import convert_base64url_to_string, convert_jwk_to_public_key_pem
from package.jwt_management.data_models.base_models import JWK
from typing import Optional

ALGORITHM = "RS256" # asymetric cryptography

class BaseClient(BaseModel):
    @classmethod
    def reverse(cls, partial_signature:str):
        converted_string = convert_base64url_to_string(partial_signature)
        return cls.model_validate_json(converted_string)

# clear
class ClientHeaders(BaseClient):
    typ:Optional[str] = Field(description="value must be only 'dpop+jwt'", default=None)
    alg:Optional[str] = Field(description="value must be only 'R256'", default=None)
    jwk:Optional[JWK] = Field(description="", default=None)
    
    @classmethod
    def from_key(cls, key):
        return cls(jwk=JWK.from_key(key))


    # @field_validator('alg', mode="before")
    # def validate_alg(cls, value:str)->str:
    #     available_algorithm = ["RS256"]
    #     if value not in available_algorithm:
    #         raise HTTPException(status_code=400, detail=f"alg must be in {available_algorithm}, instead '{value}")
    #     return value
    
    # @field_validator('typ', mode="before")
    # def validate_typ(cls, value:str)->str:
    #     availables = ["dpop+jwt"]
    #     if value not in availables:
    #         raise HTTPException(status_code=400, detail=f"typ must be in {availables}, instead '{value}")
    #     return value
    
    @classmethod
    def verify_dpop_headers(cls, headers:dict):
        header_dict = headers
        targets = dict(zip(["typ", "alg", "jwk"],["dpop+jwt", "RS256", {}]))
        for header, value in targets.items():
            val = header_dict.get(header, None)
            if val==None:
                raise HTTPException(status_code=400, detail=f"Unexpected error: {header} is missing from DPoP headers.")
            if (val!=value) and (not isinstance(value, dict)):
                raise HTTPException(status_code=400, detail=f"Unexpected error: headers '{header}' was invalid.")
            

class ClientClaims(BaseClient):
    jti:Optional[str] = Field(description="", default=None)
    iat:Optional[int] = Field(description="", default=None)
    exp:Optional[int] = Field(description="", default=None)
    htm:Optional[str] = Field(description="", default=None)
    htu:Optional[str] = Field(description="", default=None)
    client_id:Optional[str] = Field(description="", default=None)
    
    def validate_method_endpoint(self, method:str, endpoint:str)->None:
        invalid_method = method.lower().endswith(self.htm.lower())
        invalid_endpoint = endpoint.lower().endswith(self.htu.lower())
        if (invalid_method==False) & (invalid_endpoint==False):
            raise HTTPException(status_code=400, detail="http method and endpoint mismatched.")
        if invalid_method==False:
            raise HTTPException(status_code=400, detail="http method mismatched.")
        if invalid_endpoint==False:
            raise HTTPException(status_code=400, detail="http endpoint mismatched.")
    
    @classmethod
    def verify_dpop_claims(cls, claims:dict):
        claim_dict = claims
        additional_claims = ["jti", "iat", "exp", "htm", "htu", "client_id"]
        for claim in additional_claims:
            if claim_dict.get(claim, None)==None:
                raise HTTPException(status_code=400, detail=f"Unexpected error: {claim} is missing from DPoP claims.")

#clear
class ClientSignature(BaseModel):
    headers:ClientHeaders
    claims:ClientClaims

    def sign(self, key:bytes)->str:
        headers = self.headers.model_dump()
        claims = self.claims.model_dump()
        return jwt.encode(claims=claims, headers=headers, key=key, algorithm=ALGORITHM)

    @classmethod
    def verify_signature(cls, signature:str):
        h, c, s = signature.split(".")
        headers = ClientHeaders.reverse(h)
        claims = ClientClaims.reverse(c)
        ClientHeaders.verify_dpop_headers(headers.model_dump())
        ClientClaims.verify_dpop_claims(claims.model_dump())
        key = convert_jwk_to_public_key_pem(headers.jwk.model_dump())
        try:
            jwt.decode(
                token=signature,
                key=key,
                algorithms=ALGORITHM,
            )   
            return cls(headers=headers, claims=claims)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unexpected error: {e}")