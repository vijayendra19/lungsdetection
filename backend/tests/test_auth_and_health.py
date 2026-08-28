def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_user_registration_and_login_flow(client):
    # 1. Register User
    reg_payload = {
        "email": "dr.smith@hospital.org",
        "password": "SecurePassword123!",
        "full_name": "Dr. Sarah Smith",
        "role": "clinician",
    }
    reg_response = client.post("/api/auth/register", json=reg_payload)
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["email"] == reg_payload["email"]
    assert user_data["full_name"] == reg_payload["full_name"]
    assert "id" in user_data

    # Duplicate registration should fail
    dup_response = client.post("/api/auth/register", json=reg_payload)
    assert dup_response.status_code == 400

    # 2. Login User
    login_payload = {
        "email": "dr.smith@hospital.org",
        "password": "SecurePassword123!",
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Bad password should fail
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "dr.smith@hospital.org", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401

    # 3. Authenticated /me endpoint
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "dr.smith@hospital.org"

    # 4. Token Refresh
    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
