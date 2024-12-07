import pytest
from package.jwt_management.data_models.client_models import ClientHeaders, ClientClaims, ClientSignature
from package.jwt_management.data_models.base_models import JWK
from package.routes.authorizer.utils import generate_code_challenge, generate_code_verifier
import time
import uuid
from package.keypair_management import KeyPairManagement

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

@pytest.fixture
def get_test_user():
    return {"username": "testusername", "password": "testpassword"}

@pytest.fixture
def get_code():
    code_verifier = generate_code_verifier(seed=555)
    code_challenge = generate_code_challenge(code_verifier=code_verifier)
    return {
        "code_challenge": code_challenge,
        "code_verifier": code_verifier
    }

@pytest.fixture
def get_client_id():
    return "testclientid"

@pytest.fixture
def get_login_data(client, get_test_user, get_code):
    headers = {}
    payload = get_test_user
    payload["code_challenge"] = get_code["code_challenge"]
    return client.post("/authorizer/login", headers=headers, json=payload)

def get_dpop_data(htm, htu):
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=KeyPairManagement(directory='./client_keypair'),
        jti=str(uuid.uuid4()),
        iat=iat,
        exp=iat+15,
        htm=htm,
        htu=htu,
        client_id="testclientid"
    )
    return c_sig, signature