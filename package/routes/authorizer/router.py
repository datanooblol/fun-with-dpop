from fastapi import APIRouter
from fastapi import Depends
from package.jwt_management import ServerJWTManagement, JWTValidation
from package.keypair_management import KeyPairManagement
from package.routes.utils import get_jwt_management, extract_dpop_proof, validate_claims, DPoPFormat, validate_refresh_token, get_tokens

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

@router.get("/token")
async def get_token(
    dpop:DPoPFormat = Depends(extract_dpop_proof)
):
    validate_claims(method="GET", uri=f"/token", claims=dpop.payload)
    client_id = dpop.payload['client_id']
    client_public_jwk = dpop.headers['jwk']
    thumbprint = server.encode_public_key_jwk_thumprint(client_public_jwk)
    return_tokens = get_tokens(client_id, thumbprint, km.load_private_key_from_pem())
    return return_tokens


@router.get("/refresh")
async def get_new_token(
    refresh_token:str=Depends(validate_refresh_token), 
    dpop:DPoPFormat = Depends(extract_dpop_proof), 
    server:ServerJWTManagement=Depends(get_jwt_management)
):
    validate_claims(method="GET", uri=f"/refresh", claims=dpop.payload)
    client_id = dpop.payload['client_id']
    client_public_jwk = dpop.headers['jwk']
    thumbprint = server.encode_public_key_jwk_thumprint(client_public_jwk)
    return_tokens = get_tokens(client_id, thumbprint, km.load_private_key_from_pem())
    return return_tokens

@router.get("/public-key")
async def show_public_key(server: ServerJWTManagement=Depends(get_jwt_management)):
    public_key_jwk = server.convert_pem_to_jwk(km.load_public_key_from_pem())
    return public_key_jwk
