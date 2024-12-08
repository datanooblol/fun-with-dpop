import time
from tests.conftest import sign_signature
import uuid

def test_happy_path(client, client_keys, get_payload_for_endpoint_token):
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=str(uuid.uuid4()),
        iat=int(time.time()),
        exp=iat+15,
        htm="POST",
        htu="/authorizer/token",
        client_id="555"
    )
    headers = {"DPoP": signature}
    payload = get_payload_for_endpoint_token
    response = client.post("/authorizer/token", headers=headers, json=payload)
    response_dict = response.json()
    assert response.status_code == 200
    assert response_dict['token_type'] == 'DPoP'
    assert "access_token" in response_dict
    assert "refresh_token" in response_dict
    assert "expires_in" in response_dict
