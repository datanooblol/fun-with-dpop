import time
from typing import Union
# from duckdb import HTTPException
from fastapi import APIRouter, Depends, Header, HTTPException
from package.database_management.data_models import AccessTokenModel
from package.ezorm.ezcrud import EzCrud
from package.jwt_management.data_models.client_models import ClientSignature
from package.jwt_management.data_models.server_models import ServerSignature
from package.utils import get_db
from package.validation.access_token_validation import AccessTokenBody, AccessTokenHeader, validate_access_token_body, validate_access_token_headers, verify_access_token
from package.validation.dpop_validation import validate_dop_request

prefix = "/resource"
# Initialize the router
router = APIRouter(
    prefix=prefix,  # Add a common prefix to all routes in this router
    tags=["resource"],   # Group routes for documentation purposes
)

@router.get("/protected")
async def get_history(
    access_token:str=Depends(validate_access_token_headers),
    dpop:ClientSignature=Depends(validate_dop_request),
    db:EzCrud=Depends(get_db)
):
    result = verify_access_token(token=access_token)
    if isinstance(result, HTTPException):
        if "verification failed" in result.detail.lower():
            raise result
        
    check_replay = AccessTokenModel(client_id=result.client_id, jti=result.jti, access_token=access_token, active=False, remark="expired")
    replayed_records = db.Read(check_replay)
    if replayed_records.shape[0]!=0:
        for _, row in replayed_records.iterrows():
            db.Update(existing=AccessTokenModel(**row.to_dict()), new=AccessTokenModel(remark="replayed"))
        raise HTTPException(status_code=401, detail="Access token replayed.")
    if result.exp < int(time.time()):
        db.Update(
            existing=AccessTokenModel(client_id=result.client_id, jti=result.jti, access_token=access_token, active=True),
            new=AccessTokenModel(active=False, remark="expired")
        )
        raise HTTPException(status_code=401, detail="Unexpected error: access token expired.")
    

    return {"response": "access token is valid"}

