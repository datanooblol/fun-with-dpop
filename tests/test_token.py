import pytest
import time
from tests.conftest import sign_signature

def test_dpop_missing(
    client, 
):
    headers = {}
    response = client.get("/authorizer/token", headers=headers)

    assert response.status_code == 400
    assert response.json() == {"detail": "DPoP missing from request headers."}

@pytest.mark.parametrize(
        'exp, sleep, scenario',
        [
            (0, 2, 'expired'),
            (15, 0, 'tampered')
        ]
)
def test_verify_client_signature(client, client_keys, exp, sleep, scenario):
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti="555",
        iat=iat,
        exp=iat+exp,
        htm="GET",
        htu="/authorizer/token",
        client_id="555"
    )
    time.sleep(sleep)
    if scenario=='expired':
        status_code = 400
        expected_response = {"detail": "Unexpected error: Signature has expired."}
    if scenario=='tampered':
        tampered_sig, tampered_signature = sign_signature(
            client_keys=client_keys,
            jti="666",
            iat=iat,
            exp=iat+exp,
            htm="GET",
            htu="/authorizer/token",
            client_id="555"
        )
        h, _, s = signature.split(".")
        _, c, _ = tampered_signature.split(".")
        signature = ".".join([h,c,s])
        status_code = 400
        expected_response = {"detail": "Unexpected error: Signature verification failed."}
    
    headers = {
        "DPoP": signature
    }
    
    response = client.get("/authorizer/token", headers=headers)
    assert response.status_code == status_code
    assert response.json() == expected_response
