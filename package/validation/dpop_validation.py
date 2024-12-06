from fastapi import Request, HTTPException
from package.jwt_management.data_models.client_models import ClientSignature
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
    return ClientSignature.verify_signature(signature=dpop_signature)


