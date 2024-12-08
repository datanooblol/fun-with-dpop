from tests.conftest import sign_signature
import time

def test_replay(client, client_keys, get_payload_for_endpoint_token):
    jti = "testreplay"
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=jti,
        iat=iat,
        exp=iat+15,
        htm="POST",
        htu="/authorizer/token",
        client_id="555",

    )
    headers = {"DPoP": signature}
    payload = get_payload_for_endpoint_token
    response = client.post("/authorizer/token", headers=headers, json=payload)
    headers = {"DPoP": signature}
    response = client.post("/authorizer/token", headers=headers, json=payload)
    assert response.status_code == 401
    assert response.json() == {"detail": "Security breach: DPoP replayed."}
