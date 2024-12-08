import pytest

from tests.conftest import get_dpop_data


@pytest.mark.parametrize(
        'scenario',
        [
            ('grant_type'),
            ('client_id'),
            ('refresh_token')
        ]
)
def test_refresh_token_body_missing(client, get_payload_for_endpoint_refresh, scenario):
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/refresh")
    payload = get_payload_for_endpoint_refresh
    headers = {"DPoP": signature}
    payload.update({"refresh_token": "mock refreshtoken"})
    payload.pop(scenario)
    response = client.post("/authorizer/refresh", headers=headers, json=payload)
    error_message = {
        "grant_type": "grant_type missing from request body.",
        "client_id": "client_id missing from request body.",
        "refresh_token": "refresh_token missing from request body.",
    }[scenario]
    assert response.status_code == 400
    assert response.json() == {"detail": error_message}

def test_refresh_token_body_invalid_grant_type(client, get_payload_for_endpoint_refresh):
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/refresh")
    payload = get_payload_for_endpoint_refresh
    headers = {"DPoP": signature}
    payload.update({"grant_type": "not refresh_token", "refresh_token": "mockrefrshtoken"})
    response = client.post("/authorizer/refresh", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid grant_type."}

