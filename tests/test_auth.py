def test_register_creates_user(client, user_payload):
    res = client.post("/auth/register", json=user_payload)
    assert res.status_code == 201, res.text
    data = res.json()

    assert data["email"] == user_payload["email"]
    assert data["username"] == user_payload["username"]
    assert "password_hash" not in data
    assert "created_at" in data

def test_login_returns_token(client, user_payload, register_user):
    res = client.post(
        "/auth/login",
        data={"username":user_payload["username"], "password":user_payload["password"]},
        headers={"Content-Type":"application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200, res.text
    data = res.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)

def test_auth_me_returns_current_user(client, auth_headers, user_payload):
    res = client.get("/auth/me", headers=auth_headers)
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["email"] == user_payload["email"]
    assert data["username"] == user_payload["username"]