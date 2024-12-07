from package.jwt_management.data_models.base_models import JWK
from tests.conftest import get_dpop_data
from package.routes.authorizer.utils import server_generate_tokens

def test_tampered(
        client, 
        client_keys, 
        server_keys,
        get_test_user,
        get_client_id,
        get_code,
        get_login_data
):
    """
    Steps:
        - client get access token from server
        - server generate access token and save
        - server return generated access token and others
        - generate fake access token
        - pack real and fake access token
        - cleint test /resource/protected
        - server validate access token
        - deny and send detail response
    """
    response = get_login_data
    response = response.json()
    code = response.get("code", None)
    c_sig, signature = get_dpop_data(htm="POST", htu="/authorizer/token")
    headers = {
        "DPoP": signature,
    }
    payload = {
        "grant_type": "authorization_code", # for /authorizer/refresh -> literal "refresh_token"
        "client_id": get_client_id, # for /authorizer/refresh
        "code": code,
        # "redirect_uri": "", # not use
        "code_verifier": get_code["code_verifier"],
        # "refresh_token": "", # for /authorizer/refresh
    }
    response = client.post("/authorizer/token", headers=headers, json=payload)
    access_token = response.json().get("access_token", None)
    
    c_sig, signature = get_dpop_data(htm="GET", htu="/resource/protected")

    thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
    tampered_access_token = server_generate_tokens(
        client_id="tampered", 
        thumbprint=thumbprint, 
        private_key=server_keys.load_private_key_from_pem(),
        ACCESS_TOKEN_LIVE=60*60, 
        REFRESH_TOKEN_LIVE=60*60*24
    ).get("access_token", None)
    h, _, s = access_token.split(".")
    _, c, _ = tampered_access_token.split(".")
    tampered = ".".join([h,c,s])
    headers = {
        "DPoP": signature,
        "Authorization": f"DPoP {tampered}"
    }
    response = client.get("/resource/protected", headers=headers)
    assert response.status_code == 400
    assert response.json() == {'detail': 'Unexpected error: Signature verification failed.'}