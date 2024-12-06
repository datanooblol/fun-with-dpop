from package.utils import hello_package

def test_get_health(client):
    # Make a GET request to the /hello endpoint
    response = client.get("/health")
    assert response.status_code == 200  # Check the HTTP status code
    assert response.json() == {"response": "Alive!"}  # Verify the response payload

def test_post_health(client):
    user = "Bank"
    payload = {
        "user": user
    }
    response = client.post("/health/", json=payload)
    assert response.status_code == 200  # Check the HTTP status code
    assert response.json() == {"response": f"Hey {user} I'm Alive!"}  # Verify the response payload

def test_package():
    """to run this scrip successfully, we need to run it at the root of the directory"""
    assert hello_package() == "hello from package"
