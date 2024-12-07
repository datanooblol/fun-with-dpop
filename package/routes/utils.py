# import time
# import uuid
# from package.jwt_management.data_models.server_models import ServerSignature, JKT

# ACCESS_TOKEN_LIVE = 60*10 # 1 hour
# REFRESH_TOKEN_LIVE = (60*60)*24 # 1 day

# def server_generate_tokens(client_id:str, thumbprint:str, private_key:bytes):
#     iat = int(time.time())
#     jti = str(uuid.uuid4())
#     access_token = ServerSignature(
#         jti=jti, 
#         iat=iat, 
#         exp=iat+ACCESS_TOKEN_LIVE, 
#         client_id=client_id, 
#         cnf=JKT(jkt=thumbprint)
#     ).sign(key=private_key)
#     refresh_token = ServerSignature(
#         jti=jti, 
#         iat=iat, 
#         exp=iat+REFRESH_TOKEN_LIVE, 
#         client_id=client_id, 
#     ).sign(key=private_key)
#     return {
#         "access_token": access_token,
#         "token_type": "DPoP",
#         "exp": iat+ACCESS_TOKEN_LIVE,
#         "refresh_token": refresh_token
#     }

# from package.jwt_management import ServerJWTManagement, JWTValidation
# from fastapi import HTTPException, Request
# import requests
# from pydantic import BaseModel
# from package.database_management import token_store
# from package._utils import config
# from functools import partial
# import uuid
# import time

import requests
from package import skm, BASE_URL
from package.jwt_management.data_models.base_models import JWK

def get_server_public_key():
    try:
        return requests.get(f"{BASE_URL}/authorizer/public-key",).json()
    except:
        return JWK.from_key(key=skm.load_public_key_from_pem()).model_dump()

# def get_jwt_management():
#     return ServerJWTManagement()

# def get_jwt_validation():
#     return JWTValidation()

# server = get_jwt_management()
# validator = get_jwt_validation()

# def get_tokens(client_id, thumbprint, private_key):    
#     iat = int(time.time())

#     access_token_jti = str(uuid.uuid4())
#     exp = iat+config.ACCESS_TOKEN_TIME
#     access_token = server.generate_token(
#         jti=access_token_jti,
#         iat=iat, 
#         exp=exp,
#         private_key=private_key,
#         algorithm=server.algorithm,
#         data={
#             "client_id": client_id, 
#             "cnf":{"jkt":thumbprint}
#         }
#     )
#     token_store.disable_token(table=config.ACCESS_TOKEN_JTI, client_id=client_id)
#     token_store.add_token(table=config.ACCESS_TOKEN_JTI, jti=access_token_jti, token=access_token, client_id=client_id, exp=exp, active=True, remark="valid")

#     refresh_token_jti = str(uuid.uuid4())
#     exp = iat+config.REFRESH_TOKEN_TIME
#     refresh_token = server.generate_token(
#         jti=refresh_token_jti,
#         iat=iat, 
#         exp=exp,
#         private_key=private_key,
#         algorithm=server.algorithm,
#         data={
#             "client_id":client_id
#         }
#     )
#     token_store.disable_token(table=config.REFRESH_TOKEN_JTI, client_id=client_id)
#     token_store.add_token(table=config.REFRESH_TOKEN_JTI, jti=refresh_token_jti, token=refresh_token, client_id=client_id, exp=exp, active=True, remark="valid")
#     return {
#         "access_token": access_token,
#         "token_type": "DPoP",
#         "exp": iat+config.ACCESS_TOKEN_TIME,
#         "refresh_token": refresh_token
#     }

# class DPoPFormat(BaseModel):
#     headers:dict
#     payload:dict

# def extract_dpop_proof(request: Request):
#     """
#     Custom dependency to extract DPoP proof from the request headers.
#     """
#     dpop = request.headers.get("DPoP")
#     if not dpop:
#         raise HTTPException(status_code=400, detail="DPoP proof is missing.")
    
#     validator.verify_dpop_signature(dpop)
#     headers, claims, _ = dpop.split(".")
    
#     headers = server.decode_from_jwt(headers)
#     validator.verify_dpop_headers(headers)
    
#     claims = server.decode_from_jwt(claims)
#     validator.verify_dpop_claims(claims)
    
#     jti = claims.get("jti", None)

#     if validator.dpop_is_replayed(table=config.DPOP_PROOF_JTI, jti=jti):
#         raise HTTPException(status_code=400, detail="DPoP Replay detected.")

#     token_store.add_jti(table=config.DPOP_PROOF_JTI, jti=jti)

#     return DPoPFormat(**{"headers":headers, "payload": claims})

# def validate_and_get_token(request):
#     token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(status_code=400, detail=f"access token is missing.")
#     if not token.startswith("DPoP "):
#         raise HTTPException(status_code=400, detail="Authorization: DPoP missing")
#     token = token.split("DPoP ")[-1]
#     return token

# def handle_invalid_token(queries, data, token_type):
#     for query in queries:
#         status_code = 401
#         if token_type=="refresh token":
#             token_store.execute(query, data)
#             status_code = 403
#         token_store.execute(query, data)
#     raise HTTPException(status_code=status_code, detail=f"Unauthorize: {token_type} {data[-1]}.")

# def validate_token(request: Request, token_type:dict):
#     token = validate_and_get_token(request)
#     _, claims, _ = token.split(".")
#     claims = server.decode_from_jwt(claims)
#     jti = claims.get("jti", None)
#     client_id = claims.get("client_id", None)
#     exp = claims.get("exp", None)

#     if (jti is None) | (client_id is None) | (exp is None):
#         raise HTTPException(status_code=400, detail="Invalid claims.")
    
#     server_public_key_jwk = get_server_public_key()
#     server_public_key_pem = server.convert_public_jwk_to_pem(server_public_key_jwk)
    
#     if validator.token_is_tampered(token=token, key=server_public_key_pem):
#         queries = [
#             f"UPDATE {config.REFRESH_TOKEN_JTI} SET active = ?, remark = ? WHERE client_id=='{client_id}';",
#             f"UPDATE {config.ACCESS_TOKEN_JTI} SET active = ?, remark = ? WHERE client_id=='{client_id}';"
#         ]
#         data = [False, "tampered"]
#         handle_invalid_token(queries, data, token_type)
    
#     if validator.token_is_replayed(table=config.ACCESS_TOKEN_JTI if token_type=="access token" else config.REFRESH_TOKEN_JTI, jti=jti, token=token, client_id=client_id):
#         queries = [
#             f"UPDATE {config.REFRESH_TOKEN_JTI} SET remark = ? WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}' AND active=={False};",
#             f"UPDATE {config.ACCESS_TOKEN_JTI} SET remark = ? WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}' AND active=={False};"
#         ]
#         data = ["replayed"]
#         handle_invalid_token(queries, data, token_type)

#     if validator.token_is_expired(exp=exp):
#         queries = [
#             f"UPDATE {config.REFRESH_TOKEN_JTI} SET active = ?, remark = ? WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}';",
#             f"UPDATE {config.ACCESS_TOKEN_JTI} SET active = ?, remark = ? WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}';"
#         ]
#         data = [False, "expired"]
#         handle_invalid_token(queries, data, token_type)

#     if validator.token_not_exist(table=config.ACCESS_TOKEN_JTI if token_type=="access token" else config.REFRESH_TOKEN_JTI, jti=jti, token=token, client_id=client_id, exp=exp):
#         raise HTTPException(status_code=400, detail=f"{token_type} inexist.")

#     return token

# validate_access_token = partial(validate_token, **{"token_type": "access token"})
# validate_refresh_token = partial(validate_token, **{"token_type": "refresh token"})

# def validate_claims(method, uri, claims):
#     if method.upper()!=claims['htm'] and not claims['htu'].endswith(uri):
#         raise HTTPException(status_code=400, detail="Invalid claim")
#     if method.upper()!=claims['htm']:
#         raise HTTPException(status_code=400, detail=f"Invalid claim: method mismatched.")
#     if not claims['htu'].endswith(uri):
#         raise HTTPException(status_code=400, detail=f"Invalid claim: url mismatched.")