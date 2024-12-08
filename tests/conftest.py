from typing import Generator
import duckdb
from fastapi.testclient import TestClient
import pytest
from package.ezorm.ezcrud import EzCrud
from package.jwt_management.data_models.client_models import ClientHeaders, ClientClaims, ClientSignature
from package.jwt_management.data_models.base_models import JWK
from package.routes.authorizer.utils import generate_code_challenge, generate_code_verifier
import time
import uuid
from package.keypair_management import KeyPairManagement

# def get_db() -> Generator:
#     return EzCrud(engine=duckdb, database="./db/test.db")

# @pytest.fixture
# def client():
#     from fastapi.testclient import TestClient
#     from main import app
#     return TestClient(app)

# @pytest.fixture
def mock_db() -> Generator:
    return EzCrud(engine=duckdb, database="./db/test.db")

# Create a test client for FastAPI
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    from package.utils import get_db
    # def override_get_db():
    #     yield db

    app.dependency_overrides[get_db] = mock_db
    with TestClient(app) as client:
        yield client

@pytest.fixture
def client_keys():
    from package.keypair_management import KeyPairManagement
    return KeyPairManagement(directory='./client_keypair')

@pytest.fixture
def server_keys():
    from package.keypair_management import KeyPairManagement
    return KeyPairManagement(directory='./server_keypair')

@pytest.fixture
def get_test_user():
    return {"client_id": "testclientid","username": "testusername", "password": "testpassword"}

@pytest.fixture
def get_code():
    code_verifier = generate_code_verifier(seed=555)
    code_challenge = generate_code_challenge(code_verifier=code_verifier)
    return {
        "code_challenge": code_challenge,
        "code_verifier": code_verifier
    }

@pytest.fixture
def get_login_data(client, get_test_user, get_code):
    headers = {}
    payload = get_test_user
    payload["code_challenge"] = get_code["code_challenge"]
    return client.post("/authorizer/login", headers=headers, json=payload)

@pytest.fixture
def get_payload_for_endpoint_token(get_login_data, get_code, get_test_user):
    login_data = get_login_data.json()
    code = login_data.get("code")
    code_verifier = get_code.get("code_verifier")
    test_user = get_test_user
    client_id = test_user.get("client_id")
    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "code_verifier": code_verifier
    }
    return payload

@pytest.fixture
def get_payload_for_endpoint_refresh(get_test_user):
    test_user = get_test_user
    client_id = test_user.get("client_id")
    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": None
    }
    return payload

# --- #

def sign_signature(client_keys, jti, iat, exp, htm, htu, client_id):
    c_sig = ClientSignature(
        headers=ClientHeaders(typ="dpop+jwt", alg="RS256", jwk=JWK.from_key(key=client_keys.load_public_key_from_pem())),
        claims=ClientClaims(
            jti=jti, iat=iat, exp=exp, htm=htm, htu=htu, client_id=client_id
        )
    )
    signature = c_sig.sign(key=client_keys.load_private_key_from_pem())
    return c_sig, signature

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

# ---[to dos]--- #
# get handler that return the payload for get access and refresh token


