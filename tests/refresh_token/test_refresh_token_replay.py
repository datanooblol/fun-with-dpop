import time
import uuid
from package.database_management.data_models import AccessTokenModel, RefreshTokenModel
from package.jwt_management.data_models.base_models import JWK
from package.routes.authorizer.utils import server_generate_tokens
from tests.conftest import get_dpop_data, mock_db

def test_replayed(client, client_keys, server_keys, get_test_user, get_payload_for_endpoint_refresh):
    """Replay means jti and access token in inactive records show up.
    Step:
        - verify access token, then get jti and access token and client_id
        - check that jit and access token and client_id already exist or not
        - if exist and active, do nothing
        - if exist and inactive, update remark to replay
    """
    db = mock_db()
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/refresh")
    thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
    client_id = get_test_user.get("client_id", None)
    jti = str(uuid.uuid4())
    iat = int(time.time())
    ACCESS_TOKEN_LIVE=60*10
    REFRESH_TOKEN_LIVE=-1
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
    # expires_in = tokens['expires_in']
    db.Create(AccessTokenModel(access_token=access_token, jti=jti, client_id=client_id, exp=iat+ACCESS_TOKEN_LIVE, active=False, remark="expired"))
    db.Create(RefreshTokenModel(refresh_token=refresh_token, access_token=access_token, jti=jti, client_id=client_id, exp=iat+REFRESH_TOKEN_LIVE, active=True))
    headers = {
        # "Authorization": f"DPoP {access_token}",
        "DPoP": signature
    }
    payload = get_payload_for_endpoint_refresh
    payload.update({"refresh_token": refresh_token})
    response = client.post("/authorizer/refresh", headers=headers, json=payload)
    assert response.status_code == 403
    assert response.json() == {'detail': 'Unexpected error: refresh token expired.'}