from package.jwt_management import ServerJWTManagement
from fastapi import HTTPException, Request
import requests
from pydantic import BaseModel

# access_token_lifetime = 5
access_token_lifetime = 60*10 # 60 seconds * 10 = 10 minutes
refresh_token_lifetime = 60*60*24 # 60 seconds * 60 minutes * 24 hours = 1 day

def get_server_public_key():
    return requests.get("http://localhost:8000/authorizer/public-key",).json()

def get_jwt_management():
    return ServerJWTManagement(access_token_lifetime=access_token_lifetime, refresh_token_lifetime=refresh_token_lifetime)

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
    server = get_jwt_management()
    result = server.verify_dpop(dpop)
    # if not result:
    #     raise HTTPException(status_code=400, detail="Verified signature unsuccessfully.")
    headers, payload = server.extract_headers_payload_from_jwt(dpop)
    return DPoPFormat(**{"headers":headers, "payload": payload})

def extract_access_token(request: Request):
    """
    Custom dependency to extract DPoP proof from the request headers.
    """
    access_token = request.headers.get("Authorization")
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token is missing.")
    if not access_token.startswith("DPoP "):
        raise HTTPException(status_code=400, detail="Authorization: DPoP missing")
    access_token = access_token.split("DPoP ")[-1]
    server = get_jwt_management()
    public_key_jwk = get_server_public_key()
    public_key_pem = server.decode_public_jwk_to_pem(public_key_jwk)
    result = server.verify_access_token(access_token, public_key_pem)
    # if not result:
    #     raise HTTPException(status_code=400, detail="Verified access token unsuccessfully.")
    return access_token

def validate_claims(method, uri, claims):
    if method.upper()!=claims['htm'] and not claims['htu'].endswith(uri):
        raise HTTPException(status_code=400, detail="Invalid claim")
    if method.upper()!=claims['htm']:
        raise HTTPException(status_code=400, detail=f"Invalid claim: method mismatched.")
    if not claims['htu'].endswith(uri):
        raise HTTPException(status_code=400, detail=f"Invalid claim: url mismatched.")