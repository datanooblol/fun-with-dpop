import pytest
import time
from package.jwt_management.data_models.client_models import ClientHeaders, ClientClaims, ClientSignature
from package.jwt_management.data_models.base_models import JWK
from tests.conftest import sign_signature
import uuid

@pytest.mark.parametrize(
        'scenario',
        [
            ('typ'),
            ('alg'),
            ('jwk'),
        ]
)
def test_headers_missing(
    client, client_keys, scenario, get_payload_for_endpoint_token
):
    iat = int(time.time())
    c_sig, signature = sign_signature(
        client_keys=client_keys,
        jti=str(uuid.uuid4()),
        iat=iat,
        exp=iat+15,
        htm="POST",
        htu="/authorizer/token",
        client_id="555"
    )
    headers = c_sig.headers.model_dump()
    _ = headers.pop(scenario)
    c_sig.headers = ClientHeaders(**headers)
    signature = c_sig.sign(key=client_keys.load_private_key_from_pem())
    headers = {"DPoP": signature}
    payload = get_payload_for_endpoint_token
    response = client.post("/authorizer/token", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"Unexpected error: {scenario} is missing from DPoP headers."}

@pytest.mark.parametrize(
        'scenario, typ, alg',
        [
            ('typ', "not+dpop", "R256"),
            ('alg', "dpop+jwt", "H256") # H256 is symetric algorithm, DPoP uses only R256
        ]
)
def test_headers_invalid(
    client, client_keys, scenario, typ, alg
):
    iat = int(time.time())
    c_sig = ClientSignature(
        headers=ClientHeaders(typ=typ, alg=alg, jwk=JWK.from_key(key=client_keys.load_public_key_from_pem())),
        claims=ClientClaims(
            jti=str(uuid.uuid4()),
            iat=iat,
            exp=iat+15,
            htm="POST",
            htu="/authorizer/token",
            client_id="555"
        )
    )
    signature = c_sig.sign(key=client_keys.load_private_key_from_pem())
    headers = {"DPoP":signature}
    payload = {}
    response = client.post("/authorizer/token", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"Unexpected error: headers '{scenario}' was invalid."}
