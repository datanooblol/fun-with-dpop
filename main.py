import time
import uuid
from package.dpop_verifier import DPoPVerifier
from fastapi import FastAPI, Depends, HTTPException, Request
from pydantic import BaseModel
from jose import jwt
import time
from package.dpop_verifier import DPoPVerifier

app = FastAPI()

# Example in-memory database (for demonstration)
users_db = {"testuser": {"username": "testuser", "password": "testpassword"}}

# Pydantic model for the token request body
class TokenRequest(BaseModel):
    grant_type: str
    username: str
    password: str

# Custom function to extract and validate DPoP Proof
def extract_dpop_proof(request: Request):
    """
    Custom dependency to extract DPoP proof from the request headers.
    """
    dpop_proof = request.headers.get("DPoP")
    if not dpop_proof:
        raise HTTPException(status_code=400, detail="DPoP proof is missing")
    return dpop_proof

# Token Endpoint
@app.post("/token")
async def token(
    body: TokenRequest,  # Expecting body data as TokenRequest
    dpop_proof: str = Depends(extract_dpop_proof)  # DPoP proof from headers
):
    """
    Token endpoint to issue access tokens and validate DPoP Proof.
    """
    # Initialize the DPoP Verifier with the provided DPoP proof
    verifier = DPoPVerifier(dpop_proof)
    header = verifier.header
    jwk = header['jwk']
    payload = verifier.payload
    # print("header", header)
    print("jwk", jwk)
    # print("payload", payload)
    
    try:
        # Verify the DPoP proof JWT signature
        decoded_payload = verifier.verify_signature()
        print("Decoded DPoP Proof JWT:", decoded_payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="DPoP Proof JWT has expired.")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=400, detail=f"Invalid DPoP Proof JWT: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")

    # Validate grant_type (for simplicity, we're using password grant type)
    if body.grant_type != "password":
        raise HTTPException(status_code=400, detail="Invalid grant_type")

    # Validate user credentials (this is a simple demo, use proper password hashing in production)
    user = users_db.get(body.username)

    if not user or user['password'] != body.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Issue an access token (you would replace this with your own JWT generation logic)
    access_token = jwt.encode(
        {"sub": body.username, "exp": time.time() + 3600},  # 1 hour expiration
        "your_secret_key",  # You would use a private key in production
        algorithm="HS256"
    )

    return {"access_token": access_token, "token_type": "bearer"}
