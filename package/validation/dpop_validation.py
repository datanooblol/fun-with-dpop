from fastapi import Request, HTTPException
from package.jwt_management.data_models.client_models import ClientSignature
from package.ezorm.crud import Read, Create
from package.database_management.data_models import DPoPModel
def validate_dop_request(request: Request):
    """
    Steps on JWT:
        - get token (signature)
        - verify signature
        - convert singature to headers, claims
        - validate claims.jti
    Steps on Database:
        - if jti is replayed, raise 400, DPoP Replay detected
        - if not, store
    Return headers, claims
    """
    dpop_signature = request.headers.get("DPoP", None)
    if dpop_signature is None:
        raise HTTPException(status_code=400, detail="DPoP missing from request headers.")
    dpop = ClientSignature.verify_signature(signature=dpop_signature)

    record = DPoPModel(jti=dpop.claims.jti)
    if Read(record).shape[0]>0:
        raise HTTPException(status_code=401, detail="Security breach: DPoP replayed.")
    Create(record)
    return dpop

