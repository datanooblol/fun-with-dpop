import pytest
import time
from tests.conftest import sign_signature
import uuid

@pytest.mark.parametrize(
        'scenario, htm, htu',
        [
            # ('happy', 'GET', '/authorizer/token'),
            ('htm_mismatched', 'POST', '/authorizer/token'),
            ('htu_mismatched', 'GET', '/authorizer/token1'),
            ('htm_htu_mismatched', 'POST', '/authorizer/token1'),
        ]
)
def test_verify_htm_htu_mismatched(client, client_keys, scenario, htm, htu):
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=str(uuid.uuid4()),
        iat=iat,
        exp=iat+15,
        htm=htm,
        htu=htu,
        client_id="555"
    )
    headers = {
        "DPoP": signature
    }
    response = client.get("/authorizer/token", headers=headers)

    if scenario == 'htu_mismatched':
        status_code = 400
        expected_response = {'detail': 'http endpoint mismatched.'}
    elif scenario == 'htm_mismatched':
        status_code = 400
        expected_response = {'detail': 'http method mismatched.'}
    elif scenario == 'htm_htu_mismatched':
        status_code = 400
        expected_response = {'detail': 'http method and endpoint mismatched.'}

    assert response.status_code == status_code
    assert response.json() == expected_response

@pytest.mark.parametrize(
        'scenario, jti, iat, exp, htm, htu, client_id',
        [
            # ("happy", True, True, True, True, True, True),
            ("jti", False, True, True, True, True, True),
            ("iat", True, False, True, True, True, True),
            ("exp", True, True, False, True, True, True),
            ("htm", True, True, True, False, True, True),
            ("htu", True, True, True, True, False, True),
            ("client_id", True, True, True, True, True, False),
        ]
)
def test_claims_missing(
    client, client_keys,
    scenario, jti, iat, exp, htm, htu, client_id
):
    _iat = int(time.time())
    
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=str(uuid.uuid4()) if jti==True else None,
        iat=_iat if iat==True else None,
        exp=_iat+15 if exp==True else None,
        htm="GET" if htm==True else None,
        htu="/authorizer/token" if htu==True else None,
        client_id="555" if client_id==True else None
    )

    headers = {
        "DPoP": signature
    }
    response = client.get("/authorizer/token", headers=headers)
    
    status_code = 400
    expected_response = {"detail": f"Unexpected error: {scenario} is missing from DPoP claims."}

    assert response.status_code == status_code
    assert response.json() == expected_response
