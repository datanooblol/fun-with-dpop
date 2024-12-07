from fastapi import Body, Request, HTTPException
from pydantic import BaseModel
from package.database_management.data_models import RefreshTokenModel
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

class RefreshTokenBody(BaseModel):
    grant_type:str
    client_id:str
    refresh_token:str

def validate_refresh_token_body(body:RefreshTokenBody=Body(...))->bool:
    if body.grant_type!="refresh_token":
        raise HTTPException(status_code=400, detail=f"Invalid grant_type.")
    if body.refresh_token is None:
        raise HTTPException(status_code=400, detail=f"refresh_token missing.")
    if body.client_id is None:
        raise HTTPException(status_code=400, detail=f"client_id missing.")
    record = Read(RefreshTokenModel(client_id=body.client_id))
    if record.shape[0]==0:
        raise HTTPException(status_code=400, detail=f"client_id not found.")

def verify_refresh_token(body:RefreshTokenBody=Body(...))->bool:
    public_key_dict = get_server_public_key()
    public_key_pem = convert_jwk_to_public_key_pem(public_key_dict)
    ServerSignature.verify_signature(signature=body.refresh_token, key=public_key_pem)
    return True