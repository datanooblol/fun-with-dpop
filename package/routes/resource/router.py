import time
from fastapi import APIRouter, Depends, HTTPException
from package.database_management.data_models import AccessTokenModel, DPoPModel
from package.ezorm.ezcrud import EzCrud
from package.jwt_management.data_models.client_models import ClientSignature
from package.utils import get_db
from package.validation.access_token_validation import validate_access_token_headers, verify_access_token
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
    # check if DPOP is replayed 
    record = DPoPModel(jti=dpop.claims.jti)
    if db.Read(record).shape[0]>0:
        raise HTTPException(status_code=401, detail="Security breach: DPoP replayed.")
    db.Create(record)
    result = verify_access_token(token=access_token)
    # if access token is tampered
    if isinstance(result, HTTPException):
        if "verification failed" in result.detail.lower():
            raise HTTPException(status_code=400, detail="Access token tampered.")
    # check if access token is replayed, replayed means a record that already expired by the server but was submit back again
    check_replay = AccessTokenModel(client_id=result.client_id, jti=result.jti, access_token=access_token, active=False, remark="expired")
    replayed_records = db.Read(check_replay)
    if replayed_records.shape[0]!=0:
        for _, row in replayed_records.iterrows():
            db.Update(existing=AccessTokenModel(**row.to_dict()), new=AccessTokenModel(remark="replayed"))
        raise HTTPException(status_code=401, detail="Access token replayed.")
    # check if access token is expired, status code 401 here is to tell client that you need to go to /authorizer/refresh
    if result.exp < int(time.time()):
        db.Update(
            existing=AccessTokenModel(client_id=result.client_id, jti=result.jti, access_token=access_token, active=True),
            new=AccessTokenModel(active=False, remark="expired")
        )
        raise HTTPException(status_code=401, detail="Access token expired.")
    
    return {"response": "access token is valid"}

