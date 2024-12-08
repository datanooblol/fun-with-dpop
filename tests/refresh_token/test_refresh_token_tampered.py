import time
import uuid

from fastapi.testclient import TestClient
from package.database_management.data_models import AccessTokenModel, RefreshTokenModel
from package.jwt_management.data_models.base_models import JWK
from package.keypair_management.base import KeyPairManagement
from package.routes.authorizer.router import REFRESH_TOKEN_LIVE
from typing import Any
from tests.conftest import get_dpop_data, mock_db
from package.routes.authorizer.utils import server_generate_tokens

def test_tampered(
        client: TestClient, 
        client_keys: KeyPairManagement, 
        server_keys: KeyPairManagement,
        get_test_user: dict[str, str],
        # get_client_id,
        get_payload_for_endpoint_refresh: dict[str, Any]
):
    """
    Steps:
        - client get access token from server
        - server generate access token and save
        - server return generated access token and others
        - generate fake access token
        - pack real and fake access token
        - cleint test /resource/protected
        - server validate access token
        - deny and send detail response
    """
    
    db = mock_db()
    jti = str(uuid.uuid4())
    iat = int(time.time())
    ACCESS_TOKEN_LIVE=60*60
    REFRESH_TOKEN_LIVE=-1
    client_id = get_test_user.get("client_id", None)
    thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
    tokens = server_generate_tokens(
        jti=jti,
        iat=iat,
        client_id=client_id, 
        thumbprint=thumbprint, 
        private_key=server_keys.load_private_key_from_pem(),
        ACCESS_TOKEN_LIVE=ACCESS_TOKEN_LIVE, 
        REFRESH_TOKEN_LIVE=REFRESH_TOKEN_LIVE
    )
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    tampered_refresh_token = server_generate_tokens(
        jti=jti,
        iat=iat,
        client_id="tampered", 
        thumbprint=thumbprint, 
        private_key=server_keys.load_private_key_from_pem(),
        ACCESS_TOKEN_LIVE=ACCESS_TOKEN_LIVE, 
        REFRESH_TOKEN_LIVE=REFRESH_TOKEN_LIVE
    )
    tampered_refresh_token = tampered_refresh_token['refresh_token']
    h, _, s = refresh_token.split(".")
    _, c, _ = tampered_refresh_token.split(".")
    tampered = ".".join([h,c,s])

    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/refresh")
    payload = get_payload_for_endpoint_refresh
    payload.update({"refresh_token":tampered})
    headers = {
        "DPoP": signature,
    }

    db.Create(AccessTokenModel(client_id=client_id, jti=jti, access_token=access_token, active=True, exp=iat+ACCESS_TOKEN_LIVE, remark="test_refresh_token_tampered"))
    db.Create(RefreshTokenModel(client_id=client_id, jti=jti, access_token=access_token, active=True, refresh_token=refresh_token, exp=iat+REFRESH_TOKEN_LIVE, remark="test_refresh_token_tampered"))

    response = client.post("/authorizer/refresh", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {'detail': 'Refresh token tampered.'}