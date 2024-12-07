# import pytest
# import time
# from tests.conftest import sign_signature
# import uuid
# def test_dpop_missing(
#     client, 
# ):
#     headers = {}
#     payload = {}
#     response = client.post("/authorizer/token", headers=headers, json=payload)

#     assert response.status_code == 400
#     assert response.json() == {"detail": "DPoP missing from request headers."}

# @pytest.mark.parametrize(
#         'scenario, exp',
#         [
#             ('expired', -1),
#             ('tampered', 15)
#         ]
# )
# def test_verify_client_signature(client, client_keys, scenario, exp):
#     iat = int(time.time())
#     c_sig, signature = sign_signature(
#         client_keys=client_keys,
#         jti=str(uuid.uuid4()),
#         iat=iat,
#         exp=iat+exp,
#         htm="POST",
#         htu="/authorizer/token",
#         client_id="555"
#     )
#     if scenario=='expired':
#         status_code = 400
#         expected_response = {"detail": "Unexpected error: Signature has expired."}
#     if scenario=='tampered':
#         tampered_sig, tampered_signature = sign_signature(
#             client_keys=client_keys,
#             jti=str(uuid.uuid4()),
#             iat=iat,
#             exp=iat+exp,
#             htm="POST",
#             htu="/authorizer/token",
#             client_id="555"
#         )
#         h, _, s = signature.split(".")
#         _, c, _ = tampered_signature.split(".")
#         signature = ".".join([h,c,s])
#         status_code = 400
#         expected_response = {"detail": "Unexpected error: Signature verification failed."}
    
#     headers = {
#         "DPoP": signature
#     }
    
#     payload = {}
#     response = client.post("/authorizer/token", headers=headers, json=payload)
#     assert response.status_code == status_code
#     assert response.json() == expected_response
