import base64
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt

class DPoPVerifier:
    def __init__(self, dpop_proof_jwt):
        """
        Initializes the DPoPVerifier with a DPoP Proof JWT.
        
        Args:
            dpop_proof_jwt (str): The DPoP Proof JWT to verify.
        """
        self.dpop_proof_jwt = dpop_proof_jwt
        self.header, self.payload = self.extract_jwt_parts()

    def base64url_decode(self, base64url):
        """
        Decode a base64url encoded string to bytes.
        
        Args:
            base64url (str): The base64url encoded string.
            
        Returns:
            bytes: The decoded byte array.
        """
        padding = '=' * (4 - len(base64url) % 4)  # Add padding to match base64 length
        return base64.urlsafe_b64decode(base64url + padding)

    def extract_jwt_parts(self):
        """
        Extract the header and payload from the DPoP Proof JWT.
        
        Returns:
            tuple: header (dict), payload (dict)
        """
        header_b64, payload_b64, _ = self.dpop_proof_jwt.split(".")
        
        header_json = self.base64url_decode(header_b64).decode('utf-8')
        payload_json = self.base64url_decode(payload_b64).decode('utf-8')
        
        header = json.loads(header_json)
        payload = json.loads(payload_json)
        
        return header, payload

    def jwk_to_rsa_public_key(self, jwk):
        """
        Convert a JWK (JSON Web Key) to an RSA public key.
        
        Args:
            jwk (dict): The JSON Web Key containing the modulus (n) and exponent (e).
            
        Returns:
            cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey: The corresponding RSA public key.
        """
        # Extract modulus (n) and exponent (e) from the JWK
        n = self.base64url_decode(jwk['n'])
        e = self.base64url_decode(jwk['e'])

        # Convert e and n to integers
        n_int = int.from_bytes(n, byteorder='big')
        e_int = int.from_bytes(e, byteorder='big')

        # Create the RSA public key using modulus n and exponent e
        public_numbers = rsa.RSAPublicNumbers(e_int, n_int)
        public_key = public_numbers.public_key()

        return public_key

    def verify_signature(self):
        """
        Verify the DPoP Proof JWT signature using the public key from the JWK in the header.
        
        Returns:
            dict: The decoded JWT payload if the signature is valid.
            
        Raises:
            jwt.ExpiredSignatureError: If the JWT has expired.
            jwt.InvalidTokenError: If the JWT is invalid.
        """
        # Extract the JWK from the JWT header
        jwk = self.header.get('jwk')

        if not jwk:
            raise ValueError("JWK is missing in the JWT header")

        # Convert the JWK to an RSA public key
        public_key = self.jwk_to_rsa_public_key(jwk)

        # Decode and verify the JWT using the public key
        decoded = jwt.decode(
            self.dpop_proof_jwt,
            public_key,
            algorithms=["RS256"],  # Ensure you're using RS256 for asymmetric signing
            audience=None,  # Optionally check if the JWT is for a specific audience
            issuer=None,  # Optionally check the issuer
            options={"verify_exp": True}  # Automatically check for the exp claim
        )

        return decoded
