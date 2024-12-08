import time
import uuid
from package.database_management.data_models import AccessTokenModel, RefreshTokenModel
from package.jwt_management.data_models.base_models import JWK
from package.routes.authorizer.utils import server_generate_tokens
from tests.conftest import get_dpop_data, mock_db

def test_expired(client, client_keys, server_keys, get_test_user):
    """
    Steps:
        - create access token
        - validate at endpoint
        - return expire
    """
    db = mock_db()
    client_id = get_test_user.get("client_id", None)
    jti = str(uuid.uuid4())
    iat = int(time.time())
    thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
    ACCESS_TOKEN_LIVE=-1
    REFRESH_TOKEN_LIVE = 60*60*24
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
    c_sig, signature = get_dpop_data(htm="GET", htu="/resource/protected")
    headers = {"Authorization": f"DPoP {access_token}", "DPoP": f"{signature}"}
    db.Create(AccessTokenModel(client_id=client_id, jti=jti, access_token=access_token, active=True, exp=iat+ACCESS_TOKEN_LIVE))
    db.Create(RefreshTokenModel(client_id=client_id, jti=jti, access_token=access_token, active=True, refresh_token=refresh_token, exp=iat+REFRESH_TOKEN_LIVE))
    response = client.get("/resource/protected", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Unexpected error: access token expired."}