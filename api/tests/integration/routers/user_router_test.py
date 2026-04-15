import pytest


def _payload(**overrides):
    data = {
        "first_name": "Joao",
        "last_name": "Silva",
        "email": "joao@example.com",
        "password": "Senha@1234",
        "password_confirm": "Senha@1234",
    }
    data.update(overrides)
    return data


def test_create_user_returns_201_and_body(client):
    response = client.post("/api/v1/users/", json=_payload())

    assert response.status_code == 201
    body = response.json()
    assert "user_id" in body


def test_create_user_rejects_password_mismatch(client):
    response = client.post(
        "/api/v1/users/",
        json=_payload(password_confirm="OutraSenha"),
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" in body
    assert any("senhas" in err.get("message", "") for err in body["detail"])

