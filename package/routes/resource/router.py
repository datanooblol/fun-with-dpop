from fastapi import APIRouter, Depends
from package.routes.utils import extract_dpop_proof, extract_access_token, validate_claims, DPoPFormat
from package.jwt_management import ServerJWTManagement

prefix = "/resource"
# Initialize the router
router = APIRouter(
    prefix=prefix,  # Add a common prefix to all routes in this router
    tags=["resource"],   # Group routes for documentation purposes
)


# Define endpoints
@router.get("/history")
async def get_history(
    access_token:str=Depends(extract_access_token),
    dpop:DPoPFormat=Depends(extract_dpop_proof),
):
    validate_claims(method="GET", uri=f"/history", claims=dpop.payload)
    return {"response": "you now get history"}

@router.post("/transfer")
async def transfer(
    access_token:str=Depends(extract_access_token),
    dpop:DPoPFormat=Depends(extract_dpop_proof),
):
    return {"response": "transfered successfully"}
