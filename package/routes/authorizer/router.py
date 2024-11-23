from fastapi import APIRouter
from fastapi import Depends
from package.jwt_management import ServerJWTManagement
from package.keypair_management import KeyPairManagement
from package.routes.utils import get_jwt_management, extract_dpop_proof, validate_claims, DPoPFormat
from pydantic import BaseModel
directory = './server_keypair'
km = KeyPairManagement(directory=directory)
km.generate_keypairs()

# Initialize the router
router = APIRouter(
    prefix="/authorizer",  # Add a common prefix to all routes in this router
    tags=["authorizer"],   # Group routes for documentation purposes
)


@router.get("/token")
async def get_token(dpop:DPoPFormat = Depends(extract_dpop_proof), server:ServerJWTManagement=Depends(get_jwt_management)):
    validate_claims(method="GET", uri=f"/token", claims=dpop.payload)
    headers, payload = dpop.headers, dpop.payload
    client_id = payload['client_id']
    client_public_jwk = headers['jwk']
    thumbprint = server.encode_public_key_jwk_thumprint(client_public_jwk)
    return_tokens = server.generate_access_refresh_token(
        private_key=km.load_private_key_from_pem(),
        thumbprint=thumbprint,
        data={"client_id": client_id}
    )
    return return_tokens

@router.get("/public-key")
async def show_public_key(server: ServerJWTManagement=Depends(get_jwt_management)):
    public_key_jwk = server.encode_pem_to_jwk(km.load_public_key_from_pem())
    return public_key_jwk
