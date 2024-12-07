import time
import uuid
from package.jwt_management.data_models.server_models import ServerSignature, JKT

def server_generate_tokens(client_id:str, thumbprint:str, private_key:bytes, ACCESS_TOKEN_LIVE:int, REFRESH_TOKEN_LIVE:int):
    jti = str(uuid.uuid4())
    iat = int(time.time())
    access_token = ServerSignature(
        jti=jti, 
        iat=iat, 
        exp=iat+ACCESS_TOKEN_LIVE, 
        client_id=client_id, 
        cnf=JKT(jkt=thumbprint)
    ).sign(key=private_key)
    refresh_token = ServerSignature(
        jti=jti, 
        iat=iat, 
        exp=iat+REFRESH_TOKEN_LIVE, 
        client_id=client_id, 
    ).sign(key=private_key)
    return {
        "access_token": access_token,
        "token_type": "DPoP",
        "exp": iat+ACCESS_TOKEN_LIVE,
        "refresh_token": refresh_token
    }