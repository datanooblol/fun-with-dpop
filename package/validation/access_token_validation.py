from fastapi import Body, Request, HTTPException
from pydantic import BaseModel
from package.database_management.data_models import AccessTokenModel
from package.ezorm.crud import Read
from package.jwt_management.data_models.server_models import ServerSignature
from package import skm
from package.routes.utils import get_server_public_key
from package.jwt_management.encode_decode import convert_jwk_to_public_key_pem

def validate_access_token_headers(request:Request)->bool:
    access_token = request.headers.get("Authorization", None)
    if access_token is None:
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization missing.")
    access_token = access_token.split(" ")
    if len(access_token)>2:
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization invalid format. Try 'DPoP accesstokenwithoutspace'")
    bearer = access_token[0]
    access_token = access_token[-1]
    if bearer.lower() != "dpop":
        raise HTTPException(status_code=400, detail=f"Invalid headers: Authorization invalid bearer. Try 'DPoP' instead of '{bearer}'.")
    return True

def verify_access_token(request:Request)->bool:
    access_token = request.headers.get("Authorization", None)
    access_token = access_token.split(" ")[-1]
    public_key_dict = get_server_public_key()
    public_key_pem = convert_jwk_to_public_key_pem(public_key_dict)
    ServerSignature.verify_signature(signature=access_token, key=public_key_pem)
    return True

class AccessTokenBody(BaseModel):
    grant_type:str
    client_id:str
    code:str
    code_verifier:str

def validate_access_token_body(body:AccessTokenBody=Body(...))->bool:
    if body.grant_type!="authorization_code":
        raise HTTPException(status_code=400, detail=f"Invalid grant_type.")
    if body.code is None:
        raise HTTPException(status_code=400, detail=f"code missing.")
    if body.code_verifier is None:
        raise HTTPException(status_code=400, detail=f"code_verifier missing.")
    if body.client_id is None:
        raise HTTPException(status_code=400, detail=f"client_id missing.")
    
    # record = Read(AccessTokenModel(client_id=body.client_id))
    # if record.shape[0]==0:
    #     raise HTTPException(status_code=400, detail=f"client_id not found.")