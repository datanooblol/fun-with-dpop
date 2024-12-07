from package.database_management.data_models import CodeModel, UserModel
from package.ezorm.crud import Create, Delete


def test_login_happy(client, get_test_user, get_code):
    headers = {}
    payload = get_test_user
    payload["code_challenge"] = get_code.get("code_challenge", None)
    response = client.post("/authorizer/login", headers=headers, json=payload)
    assert response.status_code == 200
    assert "code" in response.json()

def test_login_invalid_password(client, get_test_user):
    """
    Steps:
        - prepare data: username, password, code_challenge
        - server check check: username not found, Incorrect password, duplicated
        - if all valid then get client_id
        - server generate code and store both code and code_challenge in CodeModel using client_id
        - return code
    """
    headers = {}
    payload = get_test_user
    payload['password'] = 'invalidpassword'
    payload["code_challenge"] = "testcodechallenge"
    response = client.post("/authorizer/login", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect password."}

def test_login_user_not_found(client, get_test_user):
    """
    Steps:
        - prepare data: username, password, code_challenge
        - server check check: username not found, Incorrect password, duplicated
        - if all valid then get client_id
        - server generate code and store both code and code_challenge in CodeModel using client_id
        - return code
    """
    headers = {}
    payload = get_test_user
    payload["username"] = "notfounduser"
    payload["code_challenge"] = "testcodechallenge"
    response = client.post("/authorizer/login", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"User '{payload['username']}' not found."}

def test_client_id_duplicate(client, get_test_user, get_code):
    headers = {}
    payload = get_test_user
    payload["code_challenge"] = get_code.get("code_challenge", None)
    code_record = CodeModel(client_id="testclientid", code="testcodeduplicate", code_challenge="testcodechallengeduplicate")
    Create(code_record)
    response = client.post("/authorizer/login", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"Client duplicated."}
    Delete(code_record)