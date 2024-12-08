import pytest
from package.jwt_management.data_models.base_models import JWK
from package.routes.authorizer.utils import server_generate_tokens
# from tests.conftest import sign_signature

@pytest.mark.parametrize(
        'scenario',
        [
            ('invalid missing'),
            ('invalid format'),
            ('invalid bearer')
        ]
)
def test_headers(client, client_keys, server_keys, scenario):
    
    client_id = "555"
    thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
    tokens = server_generate_tokens(
        client_id=client_id, 
        thumbprint=thumbprint, 
        private_key=server_keys.load_private_key_from_pem(),
        ACCESS_TOKEN_LIVE=0, 
        REFRESH_TOKEN_LIVE=0
    )
    access_token = tokens["access_token"]
    headers = {"DPoP": ""}
    if scenario=='invalid missing':
        error_message = "Invalid headers: Authorization missing."
    if scenario=='invalid format':
        headers.update({
            "Authorization": f"Bearer {' '.join(access_token.split('.'))}"
        })
        error_message = "Invalid headers: Authorization invalid format. Try 'DPoP accesstokenwithoutspace'."
    if scenario=='invalid bearer':
        bearer = "Bearer"
        error_message = f"Invalid headers: Authorization invalid bearer. Try 'DPoP' instead of '{bearer}'."
        headers.update({
            "Authorization": f"{bearer} {access_token}"
        })
    response = client.get("/resource/protected", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": error_message}