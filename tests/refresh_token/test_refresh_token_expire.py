# from package.jwt_management.data_models.base_models import JWK
# from package.routes.authorizer.utils import server_generate_tokens

# def test_expired(client, client_keys, server_keys):
#     """
#     Steps:
#         - create access token
#         - validate at endpoint
#         - return expire
#     """

#     client_id = "555"
#     thumbprint = JWK.from_key(key=client_keys.load_public_key_from_pem()).to_thumbprint()
#     tokens = server_generate_tokens(
#         client_id=client_id, 
#         thumbprint=thumbprint, 
#         private_key=server_keys.load_private_key_from_pem(),
#         ACCESS_TOKEN_LIVE=0, 
#         REFRESH_TOKEN_LIVE=-1
#     )
#     refresh_token = tokens["refresh_token"]
#     headers = {"Authorization": f"DPoP {refresh_token}"}
#     response = client.get("/resource/protected", headers=headers)
#     assert response.status_code ==400
#     assert response.json() == {"detail": "Unexpected error: Signature has expired."}