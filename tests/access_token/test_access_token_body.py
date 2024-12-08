import pytest

from tests.conftest import get_dpop_data


@pytest.mark.parametrize(
        'scenario',
        [
            ('grant_type'),
            ('client_id'),
            ('code'),
            ('code_verifier')
        ]
)
def test_access_token_body_missing(client, get_payload_for_endpoint_token, scenario):
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/token")
    payload = get_payload_for_endpoint_token
    headers = {"DPoP": signature}
    payload.pop(scenario)
    response = client.post("/authorizer/token", headers=headers, json=payload)
    error_message = {
        "grant_type": "grant_type missing from request body.",
        "client_id": "client_id missing from request body.",
        "code": "code missing from request body.",
        "code_verifier": "code_verifier missing from request body.",
    }[scenario]
    assert response.status_code == 400
    assert response.json() == {"detail": error_message}

def test_access_token_body_invalid_grant_type(client, get_payload_for_endpoint_token):
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/token")
    payload = get_payload_for_endpoint_token
    headers = {"DPoP": signature}
    payload.update({"grant_type": "not authorization_code"})
    response = client.post("/authorizer/token", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid grant_type."}

