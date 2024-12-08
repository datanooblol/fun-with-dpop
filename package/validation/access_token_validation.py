from typing import Union
from fastapi import Body, Header, HTTPException, Request
from pydantic import BaseModel
from package.jwt_management.data_models.server_models import ServerSignature
from package.routes.utils import get_server_public_key
from package.jwt_management.encode_decode import convert_jwk_to_public_key_pem

class AccessTokenHeader(BaseModel):
    Authorization:str
    DPoP:str

def validate_access_token_headers(request:Request)->Union[str | HTTPException]:
    access_token = request.headers.get("Authorization", None)
    if access_token is None:
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization missing.")
    access_token = access_token.split(" ")
    if len(access_token)>2:
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization invalid format. Try 'DPoP accesstokenwithoutspace'.")
    bearer = access_token[0]
    access_token = access_token[-1]
    if bearer.lower() != "dpop":
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization invalid bearer. Try 'DPoP' instead of '{bearer}'.")
    return access_token

def verify_access_token(token:str)->Union[ServerSignature |HTTPException]:
    public_key_dict = get_server_public_key()
    public_key_pem = convert_jwk_to_public_key_pem(public_key_dict)
    return ServerSignature.verify_signature(signature=token, key=public_key_pem)

class AccessTokenBody(BaseModel):
    grant_type:str
    client_id:str
    code:str
    code_verifier:str

def validate_access_token_body(body:AccessTokenBody=Body(...))->Union[AccessTokenBody|HTTPException]:
    # body = AccessTokenBody(**request.body)
    if body.grant_type!="authorization_code":
        return HTTPException(status_code=400, detail=f"Invalid grant_type.")
    if body.code is None:
        return HTTPException(status_code=400, detail=f"code missing.")
    if body.code_verifier is None:
        return HTTPException(status_code=400, detail=f"code_verifier missing.")
    if body.client_id is None:
        return HTTPException(status_code=400, detail=f"client_id missing.")
    return body