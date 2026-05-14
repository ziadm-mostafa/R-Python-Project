def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "member"


def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "123456"
    })

    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "123456"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid(client):
    response = client.post("/auth/login", json={
        "username": "fake",
        "password": "wrong"
    })

    assert response.status_code == 401