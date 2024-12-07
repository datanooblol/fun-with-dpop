from tests.conftest import sign_signature
import time

def test_replay(client, client_keys):
    jti = "testreplay"
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=jti,
        iat=iat,
        exp=iat+15,
        htm="GET",
        htu="/authorizer/token",
        client_id="555",

    )
    headers = {"DPoP": signature}
    response = client.get("/authorizer/token", headers=headers)
    headers = {"DPoP": signature}
    response = client.get("/authorizer/token", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Security breach: DPoP replayed."}
