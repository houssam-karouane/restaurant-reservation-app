"""Tests des endpoints d'authentification et `/users/me`."""

from __future__ import annotations


# ─── /auth/register ──────────────────────────────────────────────────────────


def test_register_success(test_client):
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
            "password": "newpass123",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["username"] == "newuser"
    assert body["is_active"] is True
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(test_client, test_user):
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "username": "another",
            "full_name": "Another",
            "password": "anotherpass1",
        },
    )
    assert response.status_code == 400
    assert "déjà enregistré" in response.json()["detail"].lower()


def test_register_invalid_email(test_client):
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "username": "x",
            "full_name": "X",
            "password": "pass12345",
        },
    )
    assert response.status_code == 422


# ─── /auth/login ─────────────────────────────────────────────────────────────


def test_login_success(test_client, test_user):
    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "alicepass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 20


def test_login_wrong_password(test_client, test_user):
    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_login_unknown_user(test_client):
    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@nowhere.com", "password": "ghostpass1"},
    )
    assert response.status_code == 401


# ─── /users/me ───────────────────────────────────────────────────────────────


def test_users_me_returns_current_user(test_client, test_user, auth_headers):
    response = test_client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == test_user.email
    assert body["username"] == test_user.username
    assert body["full_name"] == test_user.full_name


def test_users_me_without_token(test_client):
    response = test_client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_users_me_invalid_token(test_client):
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not.a.valid.token"},
    )
    assert response.status_code == 401
