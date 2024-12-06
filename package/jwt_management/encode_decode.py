import base64
import json
from jwcrypto import jwk
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.serialization import PrivateFormat, PublicFormat, NoEncryption, Encoding

def convert_string_to_base64url(string:bytes)->str:
    return base64.urlsafe_b64encode(string).rstrip(b'=').decode('utf-8')

def convert_base64url_to_string(encdoded_string:str)->bytes:
    # Add padding if necessary
    padding = "=" * (4 - len(encdoded_string) % 4)
    encdoded_string += padding
    return base64.urlsafe_b64decode(encdoded_string).decode('utf-8')

def convert_key_to_jwk(key:bytes)->dict:
    jwk_key = jwk.JWK.from_pem(key)
    return jwk_key.export(as_dict=True)

def convert_jwk_to_public_key_pem(key:dict)->bytes:
    jwk_key = jwk.JWK(**key)
    pem_key = jwk_key.export_to_pem(private_key=False, password=None)

    # Convert PEM back to a public key object
    pem_key = load_pem_public_key(pem_key)
    key = pem_key.public_bytes(
                encoding=Encoding.PEM,
                format=PublicFormat.SubjectPublicKeyInfo
            )
    return key