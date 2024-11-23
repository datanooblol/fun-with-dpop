from jwcrypto import jwk
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.serialization import PrivateFormat, PublicFormat, NoEncryption, Encoding
import base64
import time
import uuid
import json
from jose import jwt, JWSError, JWTError, ExpiredSignatureError
import hashlib
from fastapi import HTTPException

class JWTBase:
    """
    Args:
        token_lifetime (int) : token_lifetime is in second
    """
    def __init__(self):
        # self.token_lifetime = token_lifetime
        self.algorithm = "RS256"

    def base64url_encode(self, string:bytes)->str:
        return base64.urlsafe_b64encode(string).rstrip(b'=').decode('utf-8')

    def base64url_decode(self, encdoded_string:str)->bytes:
        # Add padding if necessary
        padding = "=" * (4 - len(encdoded_string) % 4)
        encdoded_string += padding
        return base64.urlsafe_b64decode(encdoded_string).decode('utf-8')
    
    def extract_headers_payload_from_jwt(self, signature:str):
        headers, payload, signature = signature.split(".")
        headers = self.base64url_decode(headers)
        payload = self.base64url_decode(payload)
        headers = json.loads(headers)
        payload = json.loads(payload)
        return headers, payload

    def decode_public_jwk_to_pem(self, key:dict):
        jwk_key = jwk.JWK(**key)
        pem_key = jwk_key.export_to_pem(private_key=False, password=None)

        # Convert PEM back to a public key object
        pem_key = load_pem_public_key(pem_key)
        key = pem_key.public_bytes(
                    encoding=Encoding.PEM,
                    format=PublicFormat.SubjectPublicKeyInfo
                )
        return key
    
    def decode_private_jwk_to_pem(self, key:dict):
        jwk_key = jwk.JWK(**key)
        pem_key = jwk_key.export_to_pem(private_key=True, password=None)

        # Convert PEM back to a public key object
        pem_key = load_pem_private_key(pem_key, password=None)
        key = pem_key.private_bytes(
            encoding=Encoding.PEM,
            # this format must match your private key format at the generation stage
            format=PrivateFormat.TraditionalOpenSSL,  # Ensure PKCS#1 format
            encryption_algorithm=NoEncryption()
        )
        return key

    def encode_pem_to_jwk(self, key:bytes)->dict:
        jwk_key = jwk.JWK.from_pem(key)

        # Export the JWK as a dictionary
        jwk_dict = jwk_key.export(as_dict=True)
        return jwk_dict

class ClientJWTManagement(JWTBase):
    def __init__(self, dpop_lifetime):
        super().__init__()
        self.dpop_lifetime = dpop_lifetime
    
    def create_headers(self, public_key:str):
        public_key_jwk = self.encode_pem_to_jwk(public_key)
        headers = {
            "typ": "dpop+jwt",
            "alg": "RS256",
            "jwk": public_key_jwk
        }
        return headers
    
    def create_payload(self, method:str, uri:str, data:dict):
        jti = str(uuid.uuid4())
        # Get the current time
        iat = int(time.time())  # Issued at timestamp
        payload = {
            "htm": method.upper(),  # HTTP method (e.g., GET, POST)
            "htu": uri,     # HTTP URI of the resource
            "iat": iat,     # Issued at timestamp
            "exp": iat + self.dpop_lifetime,     # Expiration timestamp
            "jti": jti      # Unique proof identifier
        }
        payload.update(**data)
        return payload

    def sign_by_client(self, headers:dict, payload:dict, private_key:bytes):
        dpop_proof = jwt.encode(
            headers=headers,
            claims=payload,
            algorithm="RS256",
            key=private_key
        )
        return dpop_proof

class ServerJWTManagement(JWTBase):
    def __init__(self, access_token_lifetime=60*10, refresh_token_lifetime=60*60*24):
        super().__init__()
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    def verify_token(self, token:str, key:bytes, **kwargs):
        try:
            # Attempt to decode and verify the JWT signature
            decoded = jwt.decode(
                token=token,
                key=key,
                algorithms=self.algorithm,
                **kwargs
            )
            return decoded  # Return the payload if valid

        # Handle specific exceptions in order of priority
        except ExpiredSignatureError as e:
            # print("Error: The JWT has expired.")
            raise HTTPException(status_code=400, detail=f"Error: The JWT has expired. {e}")
        except JWSError as e:
            # print(f"Error: JWS error occurred. {e}")
            raise HTTPException(status_code=400, detail=f"Error: JWS error occurred. {e}")
        except JWTError as e:
            # print(f"Error: General JWT verification issue. {e}")
            raise HTTPException(status_code=400, detail=f"Error: General JWT verification issue. {e}")
        except Exception as e:
            # print(f"Unexpected error: {e}")
            raise HTTPException(status_code=400, detail=f"Unexpected error: {e}")

        # Return None if the JWT is invalid
        return None
    
    def encode_public_key_jwk_thumprint(self, public_key_jwk:dict):
        canonical_jwk = json.dumps({
            "e": public_key_jwk["e"],
            "kty": public_key_jwk["kty"],
            "n": public_key_jwk["n"]
        }, separators=(',', ':'), sort_keys=True)
        sha256_hash = hashlib.sha256(canonical_jwk.encode("utf-8")).digest()
        thumbprint = self.base64url_encode(sha256_hash)
        return thumbprint
    
    def generate_access_refresh_token(self, private_key:bytes, thumbprint:str, data:dict={})->dict:
        iat = int(time.time())  # Issued at timestamp
        payload = {
            "iat": iat,
            "exp": iat + self.refresh_token_lifetime,
        }
        payload.update(**data)
        refresh_token = jwt.encode(
            claims=payload, key=private_key, algorithm=self.algorithm
        )
        payload.update({"exp": iat + self.access_token_lifetime})
        payload.update({"cnf": {"jkt": thumbprint}})
        access_token = jwt.encode(
            claims=payload, key=private_key, algorithm=self.algorithm
        )
        return {
            "access_token": access_token,
            "token_type": "DPoP",
            "expires_in": (iat + self.access_token_lifetime) - iat,
            "refresh_token": refresh_token
        }
    
    def verify_dpop(self, signature:str):
        headers, payload = self.extract_headers_payload_from_jwt(signature)
        public_jwk = headers['jwk']
        public_key = self.decode_public_jwk_to_pem(public_jwk)
        return self.verify_token(token=signature, key=public_key, options={"verify_exp": True})

    def verify_access_token(self, access_token:str, public_key:bytes):
        result = self.verify_token(token=access_token, key=public_key, options={"verify_exp": True})
        return result
    
    def verify_refresh_token(self, refresh_token:str, public_key:bytes):
        result = self.verify_token(token=refresh_token, key=public_key, options={"verify_exp": True})
        return result



