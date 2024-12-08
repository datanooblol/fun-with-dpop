import uuid
from fastapi import APIRouter, Body
from fastapi import Depends
# from package.jwt_management import ServerJWTManagement, JWTValidation
# from package.routes.utils import get_jwt_management, extract_dpop_proof, validate_claims, DPoPFormat, validate_refresh_token, get_tokens
from package.ezorm.ezcrud import EzCrud
from package.ezorm.variables import EzORM
from package.utils import get_db
from package.validation.access_token_validation import AccessTokenBody, validate_access_token_body
from package.validation.dpop_validation import validate_dop_request
from package.jwt_management.data_models.client_models import ClientSignature
from package.routes.authorizer.utils import server_generate_tokens
from package import skm
from package.jwt_management.data_models.base_models import JWK
from fastapi.responses import JSONResponse
from package.ezorm.crud import Read, Create, Update
from package.database_management.data_models import CodeModel, LoginFormat, RegisterFormat, TestModel, UserModel
from package.validation.login_validation import validate_login_request
from package.validation.refresh_token_validation import RefreshTokenBody, validate_refresh_token_body, verify_refresh_token
from package.validation.register_validation import validate_register_request

skm.generate_keypairs()

ACCESS_TOKEN_LIVE = 60*10 # 1 hour
REFRESH_TOKEN_LIVE = (60*60)*24 # 1 day

# # Initialize the router
router = APIRouter(
    prefix="/authorizer",  # Add a common prefix to all routes in this router
    tags=["authorizer"],   # Group routes for documentation purposes
)

# jwtv = JWTValidation()
# server = ServerJWTManagement()

@router.post("/token")
async def get_token(
    dpop:ClientSignature=Depends(validate_dop_request),
    body:AccessTokenBody=Depends(validate_access_token_body)
):  
    dpop.claims.validate_method_endpoint(method="POST", endpoint="/authorizer/token")
    client_public_thumbprint = dpop.headers.jwk.to_thumbprint()
    client_id = dpop.claims.client_id
    return server_generate_tokens(
        client_id=client_id, 
        thumbprint=client_public_thumbprint, 
        private_key=skm.load_private_key_from_pem(), 
        ACCESS_TOKEN_LIVE=ACCESS_TOKEN_LIVE, 
        REFRESH_TOKEN_LIVE=REFRESH_TOKEN_LIVE
    )

# @router.post("/login")
# async def post_login(code:CodeModel=Depends(validate_login_request)):
#     """simulate login behavior"""
    
#     return JSONResponse({"code": code.code})

@router.post("/login")
async def post_login(user:LoginFormat=Body(...), db:EzCrud=Depends(get_db)):
    """simulate login behavior"""
    code:CodeModel = validate_login_request(user, db)
    return JSONResponse({"code": code.code})
    

# @router.post("/register")
# async def post_register_user(user:RegisterFormat=Depends(validate_register_request)):
#     new_user = UserModel(client_id=str(uuid.uuid4()), username=user.username, password=user.password)
#     Create(new_user)
#     return {"response": f"User '{new_user.username}' registered successfully"}

@router.post("/register")
async def post_register_user(user:RegisterFormat=Body(...), db=Depends(get_db)):
    user = validate_register_request(user, db)
    new_user = UserModel(client_id=str(uuid.uuid4()), username=user.username, password=user.password)
    db.Create(new_user)
    return {"response": f"User '{new_user.username}' registered successfully"}


@router.post("/test")
async def post_test(test:TestModel):
    return {"response": "test"}

@router.post("/refresh")
async def post_refresh(
    dpop:ClientSignature=Depends(validate_dop_request),
    body:RefreshTokenBody=Depends(validate_refresh_token_body),
    refresh_token_valid:RefreshTokenBody=Depends(verify_refresh_token),
):
    dpop.claims.validate_method_endpoint(method="POST", endpoint="/authorizer/refresh")
    client_public_thumbprint = dpop.headers.jwk.to_thumbprint()
    client_id = dpop.claims.client_id
    return server_generate_tokens(
        client_id=client_id, 
        thumbprint=client_public_thumbprint, 
        private_key=skm.load_private_key_from_pem(), 
        ACCESS_TOKEN_LIVE=ACCESS_TOKEN_LIVE, 
        REFRESH_TOKEN_LIVE=REFRESH_TOKEN_LIVE
    )
# @router.get("/refresh")
# async def get_new_token(
#     refresh_token:str=Depends(validate_refresh_token), 
#     dpop:DPoPFormat = Depends(extract_dpop_proof), 
#     server:ServerJWTManagement=Depends(get_jwt_management)
# ):
#     validate_claims(method="GET", uri=f"/refresh", claims=dpop.payload)
#     client_id = dpop.payload['client_id']
#     client_public_jwk = dpop.headers['jwk']
#     thumbprint = server.encode_public_key_jwk_thumprint(client_public_jwk)
#     return_tokens = get_tokens(client_id, thumbprint, km.load_private_key_from_pem())
#     return return_tokens

@router.get("/public-key")
async def show_public_key():
    public_key_jwk = JWK.from_key(skm.load_public_key_from_pem())
    return public_key_jwk
