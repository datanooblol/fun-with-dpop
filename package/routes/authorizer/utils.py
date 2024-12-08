import time
import uuid
from package.jwt_management.data_models.server_models import ServerSignature, JKT
import base64
import hashlib
import random
import string
import os

def server_generate_tokens(client_id:str, thumbprint:str, private_key:bytes, ACCESS_TOKEN_LIVE:int, REFRESH_TOKEN_LIVE:int, jti:str=None, iat:int=None):
    if jti is None:
        jti = str(uuid.uuid4())
    if iat is None:
        iat = int(time.time())
    access_token = ServerSignature(
        jti=jti, 
        iat=iat, 
        exp=iat+ACCESS_TOKEN_LIVE, 
        client_id=client_id, 
        cnf=JKT(jkt=thumbprint)
    ).sign(key=private_key)
    refresh_token = ServerSignature(
        jti=jti, 
        iat=iat, 
        exp=iat+REFRESH_TOKEN_LIVE, 
        client_id=client_id, 
    ).sign(key=private_key)
    return {
        "access_token": access_token,
        "token_type": "DPoP",
        "expires_in": ACCESS_TOKEN_LIVE,
        "refresh_token": refresh_token
    }



def generate_code(seed=None):
    """Generate a code (e.g., an authorization code for OAuth2)."""
    if seed is not None:
        random.seed(seed)  # Freeze the randomness with a fixed seed
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def generate_code_verifier(seed=None):
    """Generate a random code verifier (frozen with a seed)."""
    if seed is not None:
        random.seed(seed)  # Freeze the randomness with a fixed seed
    return ''.join(random.choices(string.ascii_letters + string.digits + '-._~', k=32))

def generate_code_challenge(code_verifier):
    """Generate a code challenge based on the code verifier."""
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')

# # Example Usage
# seed_value = 42  # Fixed seed for predictable randomness

# # Generate code, code_verifier, and code_challenge with the frozen randomness
# code = generate_code(seed=seed_value)
# code_verifier = generate_code_verifier(seed=seed_value)
# code_challenge = generate_code_challenge(code_verifier)

# print(f"Code: {code}")
# print(f"Code Verifier: {code_verifier}")
# print(f"Code Challenge: {code_challenge}")
