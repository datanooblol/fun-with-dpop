import time
import uuid
from fastapi import APIRouter, Body, HTTPException
from fastapi import Depends
from package.ezorm.ezcrud import EzCrud
from package.utils import get_db
from package.validation.access_token_validation import AccessTokenBody, validate_access_token_body
from package.validation.dpop_validation import validate_dop_request
from package.jwt_management.data_models.client_models import ClientSignature
from package.routes.authorizer.utils import server_generate_tokens
from package import skm
from package.jwt_management.data_models.base_models import JWK
from fastapi.responses import JSONResponse
from package.ezorm.crud import Read, Create, Update
from package.database_management.data_models import AccessTokenModel, CodeModel, LoginFormat, RefreshTokenModel, RegisterFormat, TestModel, UserModel
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

@router.post("/login")
async def post_login(user:LoginFormat=Body(...), db:EzCrud=Depends(get_db)):
    """simulate login behavior"""
    code:CodeModel = validate_login_request(user, db)
    return JSONResponse({"code": code.code})

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
    body:RefreshTokenBody,
    dpop:ClientSignature=Depends(validate_dop_request),
    db:EzCrud=Depends(get_db)
    # body:RefreshTokenBody=Depends(validate_refresh_token_body),
    # refresh_token_valid:RefreshTokenBody=Depends(verify_refresh_token),
):
    dpop.claims.validate_method_endpoint(method="POST", endpoint="/authorizer/refresh")
    validate_refresh_token_body(body, db)
    refresh_token = body.refresh_token
    result = verify_refresh_token(refresh_token)

    if isinstance(result, HTTPException):
        if "verification failed" in result.detail.lower():
            raise result

    check_replay = RefreshTokenModel(client_id=result.client_id, jti=result.jti, refresh_token=refresh_token, active=False, exp=result.exp, remark="expired")
    replayed_records = db.Read(check_replay)
    if replayed_records.shape[0]!=0:
        raise HTTPException(status_code=401, detail="Refresh token replayed.")
    if result.exp < int(time.time()):
        existing = db.Read(RefreshTokenModel(client_id=result.client_id, jti=result.jti, refresh_token=refresh_token, exp=result.exp, active=True))
        existing = RefreshTokenModel(**existing.iloc[0].to_dict())
        db.Update(
            existing=AccessTokenModel(client_id=result.client_id, access_token=existing.access_token),
            new=AccessTokenModel(active=False, remark="expired")
        )
        db.Update(
            existing=existing,
            new=RefreshTokenModel(active=False, remark="expired")
        )
        raise HTTPException(status_code=403, detail="Unexpected error: refresh token expired.")
    
    client_public_thumbprint = dpop.headers.jwk.to_thumbprint()
    client_id = dpop.claims.client_id
    return server_generate_tokens(
        client_id=client_id, 
        thumbprint=client_public_thumbprint, 
        private_key=skm.load_private_key_from_pem(), 
        ACCESS_TOKEN_LIVE=ACCESS_TOKEN_LIVE, 
        REFRESH_TOKEN_LIVE=REFRESH_TOKEN_LIVE
    )

@router.get("/public-key")
async def show_public_key():
    public_key_jwk = JWK.from_key(skm.load_public_key_from_pem())
    return public_key_jwk
