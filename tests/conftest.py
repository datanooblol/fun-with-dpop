import pytest
from package.jwt_management.data_models.client_models import ClientHeaders, ClientClaims, ClientSignature
from package.jwt_management.data_models.base_models import JWK

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)

@pytest.fixture
def client_keys():
    from package.keypair_management import KeyPairManagement
    return KeyPairManagement(directory='./client_keypair')

@pytest.fixture
def server_keys():
    from package.keypair_management import KeyPairManagement
    return KeyPairManagement(directory='./server_keypair')

def sign_signature(client_keys, jti, iat, exp, htm, htu, client_id):
    c_sig = ClientSignature(
        headers=ClientHeaders(typ="dpop+jwt", alg="RS256", jwk=JWK.from_key(key=client_keys.load_public_key_from_pem())),
        claims=ClientClaims(
            jti=jti, iat=iat, exp=exp, htm=htm, htu=htu, client_id=client_id
        )
    )
    signature = c_sig.sign(key=client_keys.load_private_key_from_pem())
    return c_sig, signature