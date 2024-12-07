from fastapi import Request, HTTPException
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