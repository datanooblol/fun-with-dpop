from fastapi import APIRouter
from fastapi import Depends
from package.jwt_management import ServerJWTManagement, JWTValidation
from package.keypair_management import KeyPairManagement
from package.database_management import token_store
from package.routes.utils import get_jwt_management, extract_dpop_proof, validate_claims, DPoPFormat, validate_refresh_token
import time
import uuid
from package.utils import config

directory = './server_keypair'
km = KeyPairManagement(directory=directory)
km.generate_keypairs()

# Initialize the router
router = APIRouter(
    prefix="/authorizer",  # Add a common prefix to all routes in this router
    tags=["authorizer"],   # Group routes for documentation purposes
)

jwtv = JWTValidation()
server = ServerJWTManagement()

def get_tokens(client_id, thumbprint):    
    iat = int(time.time())

    access_token_jti = str(uuid.uuid4())
    exp = iat+config.ACCESS_TOKEN_TIME
    access_token = server.generate_token(
        jti=access_token_jti,
        iat=iat, 
        exp=exp,
        private_key=km.load_private_key_from_pem(),
        algorithm=server.algorithm,
        data={
            "client_id": client_id, 
            "cnf":{"jkt":thumbprint}
        }
    )
    token_store.add_token(table=config.ACCESS_TOKEN_JTI, jti=access_token_jti, token=access_token, client_id=client_id, exp=exp, active=True)

    refresh_token_jti = str(uuid.uuid4())
    exp = iat+config.REFRESH_TOKEN_TIME
    refresh_token = server.generate_token(
        jti=refresh_token_jti,
        iat=iat, 
        exp=exp,
        private_key=km.load_private_key_from_pem(),
        algorithm=server.algorithm,
        data={
            "client_id":client_id
        }
    )
    token_store.add_token(table=config.REFRESH_TOKEN_JTI, jti=refresh_token_jti, token=refresh_token, client_id=client_id, exp=exp, active=True)
    print("access token exp: ", iat+config.ACCESS_TOKEN_TIME)
    return {
        "access_token": access_token,
        "token_type": "DPoP",
        "exp": iat+config.ACCESS_TOKEN_TIME,
        "refresh_token": refresh_token
    }

@router.get("/token")
async def get_token(
    dpop:DPoPFormat = Depends(extract_dpop_proof)
):
    validate_claims(method="GET", uri=f"/token", claims=dpop.payload)
    client_id = dpop.payload['client_id']
    client_public_jwk = dpop.headers['jwk']
    thumbprint = server.encode_public_key_jwk_thumprint(client_public_jwk)
    return_tokens = get_tokens(client_id, thumbprint)
    return return_tokens


@router.get("/refresh")
async def get_new_token(
    refresh_token:str=Depends(validate_refresh_token), 
    dpop:DPoPFormat = Depends(extract_dpop_proof), 
    server:ServerJWTManagement=Depends(get_jwt_management)
):
    validate_claims(method="GET", uri=f"/refresh", claims=dpop.payload)
    # jti, token, client_id to update active
    # create access and refresh token
    # update access and refresh active status
    return {"response": "refresh"}

@router.get("/public-key")
async def show_public_key(server: ServerJWTManagement=Depends(get_jwt_management)):
    public_key_jwk = server.convert_pem_to_jwk(km.load_public_key_from_pem())
    return public_key_jwk
