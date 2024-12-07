import pytest
import time
from tests.conftest import sign_signature
import uuid
def test_dpop_missing(
    client, 
):
    headers = {}
    payload = {}
    response = client.post("/authorizer/token", headers=headers, json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "DPoP missing from request headers."}
