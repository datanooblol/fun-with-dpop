from fastapi import Request, HTTPException

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
    dpop = request.headers.get("DPoP", None)
    return dpop


