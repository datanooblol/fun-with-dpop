import pytest
import time
from tests.conftest import sign_signature
import uuid
def test_dpop_missing(
    client, get_payload_for_endpoint_token
):
    headers = {}
    payload = get_payload_for_endpoint_token
    response = client.post("/authorizer/token", headers=headers, json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "DPoP missing from request headers."}