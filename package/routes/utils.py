from package.jwt_management import ServerJWTManagement, JWTValidation
from fastapi import HTTPException, Request
import requests
from pydantic import BaseModel
from package.database_management import token_store
from package.utils import config
from functools import partial


def get_server_public_key():
    return requests.get("http://localhost:8000/authorizer/public-key",).json()

def get_jwt_management():
    return ServerJWTManagement()

def get_jwt_validation():
    return JWTValidation()

server = get_jwt_management()
validator = get_jwt_validation()

class DPoPFormat(BaseModel):
    headers:dict
    payload:dict

def extract_dpop_proof(request: Request):
    """
    Custom dependency to extract DPoP proof from the request headers.
    """
    dpop = request.headers.get("DPoP")
    if not dpop:
        raise HTTPException(status_code=400, detail="DPoP proof is missing.")
    validator.verify_dpop_signature(dpop)
    headers, claims, _ = dpop.split(".")
    claims = server.decode_from_jwt(claims)
    
    jti = claims.get("jti", None)
    if (jti is not None):
        token_store.dpop_is_unique(table=config.DPOP_PROOF_JTI, jti=jti)

    validator.verify_dpop_payload(claims)
    headers = server.decode_from_jwt(headers)
    validator.verify_dpop_headers(headers)

    return DPoPFormat(**{"headers":headers, "payload": claims})

def validate_token(request: Request, token_type:str):
    """
    Custom dependency to extract DPoP proof from the request headers.
    """
    if token_type=='access token':
        table = config.ACCESS_TOKEN_JTI
    else:
        table = config.REFRESH_TOKEN_JTI

    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=400, detail=f"{token_type} is missing.")
    if not token.startswith("DPoP "):
        raise HTTPException(status_code=400, detail="Authorization: DPoP missing")
    
    token = token.split("DPoP ")[-1]

    server_public_key_jwk = get_server_public_key()
    server_public_key_pem = server.convert_public_jwk_to_pem(server_public_key_jwk)
    
    claims = validator.verify_token(token, server_public_key_pem, token_type=token_type, options={"verify_exp": True})
    jti = claims.get("jti", None)
    client_id = claims.get("client_id", None)
    exp = claims.get("exp", None)
    token_store.token_is_valid(table=table, jti=jti, token=token, client_id=client_id, exp=exp)
    return token

validate_access_token = partial(validate_token, **{"token_type": "access token"})
validate_refresh_token = partial(validate_token, **{"token_type": "refresh token"})

def validate_claims(method, uri, claims):
    if method.upper()!=claims['htm'] and not claims['htu'].endswith(uri):
        raise HTTPException(status_code=400, detail="Invalid claim")
    if method.upper()!=claims['htm']:
        raise HTTPException(status_code=400, detail=f"Invalid claim: method mismatched.")
    if not claims['htu'].endswith(uri):
        raise HTTPException(status_code=400, detail=f"Invalid claim: url mismatched.")