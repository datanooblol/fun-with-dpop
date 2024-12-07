from fastapi import APIRouter, Depends
from package.validation.access_token_validation import validate_access_token_headers, verify_access_token
# from package.routes.utils import extract_dpop_proof, validate_claims, validate_access_token, DPoPFormat
# from package.jwt_management import ServerJWTManagement

prefix = "/resource"
# Initialize the router
router = APIRouter(
    prefix=prefix,  # Add a common prefix to all routes in this router
    tags=["resource"],   # Group routes for documentation purposes
)

@router.get("/protected")
async def get_history(
    header_is_valid=Depends(validate_access_token_headers),
    access_token_is_valid=Depends(verify_access_token)
):
    return {"response": "access token is valid"}

# # Define endpoints
# @router.get("/history")
# async def get_history(
#     access_token:str=Depends(validate_access_token),
#     dpop:DPoPFormat=Depends(extract_dpop_proof),
# ):
#     validate_claims(method="GET", uri=f"/history", claims=dpop.payload)
#     return {"response": "you now get history"}

# @router.post("/transfer")
# async def transfer(
#     access_token:str=Depends(validate_access_token),
#     dpop:DPoPFormat=Depends(extract_dpop_proof),
# ):
#     return {"response": "transfered successfully"}
