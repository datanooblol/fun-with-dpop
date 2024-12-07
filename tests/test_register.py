from package.ezorm.crud import Delete
from package.database_management.data_models import UserModel

def test_happy_path_register(client, get_test_user):
    headers = {}
    payload = {
        "username": "testnewuser",
        "password": "testnewpassword"
    }
    response = client.post("/authorizer/register", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json() == {"response": f"User '{payload['username']}' registered successfully"}
    Delete(UserModel(username=payload["username"], password=payload["password"]))

def test_register_user_exists(client, get_test_user):
    headers = {}
    payload = get_test_user
    response = client.post("/authorizer/register", headers=headers, json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"User '{payload['username']}' already exists"}