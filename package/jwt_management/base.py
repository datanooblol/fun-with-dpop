from jwcrypto import jwk
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.serialization import PrivateFormat, PublicFormat, NoEncryption, Encoding
import base64
from package.database_management import token_store
import json
from jose import jwt, JWSError, JWTError, ExpiredSignatureError
import hashlib
from fastapi import HTTPException
import time

class JWTBase:
    """
    Args:
        token_lifetime (int) : token_lifetime is in second
    """
    def __init__(self):
        self.algorithm = "RS256"

    def base64url_encode(self, string:bytes)->str:
        return base64.urlsafe_b64encode(string).rstrip(b'=').decode('utf-8')

    def base64url_decode(self, encdoded_string:str)->bytes:
        # Add padding if necessary
        padding = "=" * (4 - len(encdoded_string) % 4)
        encdoded_string += padding
        return base64.urlsafe_b64decode(encdoded_string).decode('utf-8')
    
    def decode_from_jwt(self, text:str)->dict:
        text = self.base64url_decode(text)
        return json.loads(text)

    def convert_public_jwk_to_pem(self, key:dict):
        jwk_key = jwk.JWK(**key)
        pem_key = jwk_key.export_to_pem(private_key=False, password=None)

        # Convert PEM back to a public key object
        pem_key = load_pem_public_key(pem_key)
        key = pem_key.public_bytes(
                    encoding=Encoding.PEM,
                    format=PublicFormat.SubjectPublicKeyInfo
                )
        return key
    
    def convert_private_jwk_to_pem(self, key:dict):
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

    def convert_pem_to_jwk(self, key:bytes)->dict:
        jwk_key = jwk.JWK.from_pem(key)

        # Export the JWK as a dictionary
        jwk_dict = jwk_key.export(as_dict=True)
        return jwk_dict

from package.data_models.Types import ClientHeaders, ClientPayload

class ClientJWTManagement(JWTBase):
    def __init__(self):
        super().__init__()
    
    def create_headers(self, public_key:bytes):
        public_key_jwk = self.convert_pem_to_jwk(public_key)
        # headers = {
        #     "typ": "dpop+jwt",
        #     "alg": "RS256",
        #     "jwk": public_key_jwk
        # }
        headers = ClientHeaders(jwk=public_key_jwk)
        return headers
    
    def create_payload(self, jti:str, iat:int, exp:int, method:str, uri:str, data:dict):
        payload = {
            "htm": method.upper(),  # HTTP method (e.g., GET, POST)
            "htu": uri,     # HTTP URI of the resource
            "iat": iat,     # Issued at timestamp
            "exp": exp,     # Expiration timestamp
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
    def __init__(self):
        super().__init__()
    
    def encode_public_key_jwk_thumprint(self, public_key_jwk:dict):
        canonical_jwk = json.dumps({
            "e": public_key_jwk["e"],
            "kty": public_key_jwk["kty"],
            "n": public_key_jwk["n"]
        }, separators=(',', ':'), sort_keys=True)
        sha256_hash = hashlib.sha256(canonical_jwk.encode("utf-8")).digest()
        thumbprint = self.base64url_encode(sha256_hash)
        return thumbprint

    def generate_token(self, jti:str, iat:int, exp:int, private_key:bytes, algorithm:str, data:dict={}):
        claims = {
            "iat": iat,
            "exp": exp,
            "jti": jti,
        }
        claims.update(**data)
        return jwt.encode(
            claims=claims, key=private_key, algorithm=algorithm
        )
    
class JWTValidation(JWTBase):
    def __init__(self,):
        super().__init__()
        self.status_code = {"dpop": 400, "access token": 401, "refresh token": 403}
    def verify_token(self, token:str, key:bytes, token_type:str, **kwargs):
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
            raise HTTPException(status_code=401, detail=f"{token_type} error: {e}")
        except JWSError as e:
            # print(f"Error: JWS error occurred. {e}")
            raise HTTPException(status_code=400, detail=f"Error: JWS error occurred. {e}")
        except JWTError as e:
            # print(f"Error: General JWT verification issue. {e}")
            raise HTTPException(status_code=400, detail=f"Error: General {token_type} verification issue. {e}")
        except Exception as e:
            # print(f"Unexpected error: {e}")
            raise HTTPException(status_code=400, detail=f"Unexpected error: {e}")

        # Return None if the JWT is invalid
        return None

    def verify_dpop_headers(self, headers:dict)->None:
        if headers['alg']!="RS256" or headers['jwk']['kty']!="RSA":
            raise HTTPException(status_code=400, detail="algorithm mismatched")
        if headers['typ']!="dpop+jwt":
            raise HTTPException(status_code=400, detail="typ mismatched")

    def verify_dpop_claims(self, claims:dict, )->None:
        if "jti" not in claims:
            raise HTTPException(status_code=400, detail="jti missing.")
        if "htu" not in claims:
            raise HTTPException(status_code=400, detail="endpoint missing.")
        if "htm" not in claims:
            raise HTTPException(status_code=400, detail="method missing.")
        if "iat" not in claims:
            raise HTTPException(status_code=400, detail="issued at missing.")
        if "exp" not in claims:
            raise HTTPException(status_code=400, detail="expired at missing.")
        if "client_id" not in claims:
            raise HTTPException(status_code=400, detail="client_id missing.")
        
    def verify_dpop_signature(self, signature:str):
        headers, _, _ = signature.split(".")
        headers = self.decode_from_jwt(headers)
        public_jwk = headers['jwk']
        public_key = self.convert_public_jwk_to_pem(public_jwk)
        return self.verify_token(token=signature, key=public_key, token_type="DPoP Proof JWT", options={"verify_exp": True})
    
    def token_is_tampered(self, token, key):
        try:
            claims = jwt.decode(
                token=token,
                key=key,
                algorithms=self.algorithm,
                options={"verify_exp": False}
            )
            return False
        except Exception as e:
            return True

    def dpop_is_replayed(self, table, jti):
        query = f"SELECT * FROM {table} WHERE jti=='{jti}'"
        df = token_store.query(query)
        if df.shape[0]>0:
            return True
        return False

    def token_is_replayed(self, table, jti, token, client_id):
        query = f"SELECT * FROM {table} WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}' AND active=={False};"
        df = token_store.query(query)
        if df.shape[0]>0:
            return True
        return False

    def token_is_expired(self, exp):
        if exp < int(time.time()):
            return True
        return False
    
    def token_not_exist(self, table, jti, token, client_id, exp):
        query = f"SELECT * FROM {table} WHERE jti=='{jti}' AND token=='{token}' AND client_id=='{client_id}' AND exp=={exp} AND active=={True};"
        df = token_store.query(query)
        if df.shape[0]==0:
            return True
        return False



