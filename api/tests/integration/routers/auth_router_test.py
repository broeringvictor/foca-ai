from tests.factories.user import DEFAULT_PASSWORD


def _payload(**overrides):
    data = {
        "email": "joao@example.com",
        "password": DEFAULT_PASSWORD,
    }
    data.update(overrides)
    return data


def _create_user(client):
    client.post(
        "/api/v1/users/",
        json={
            "first_name": "Joao",
            "last_name": "Silva",
            "email": "joao@example.com",
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
        },
    )


class TestAuthenticateRouter:
    def test_returns_200_and_token(self, client):
        _create_user(client)
        response = client.post("/api/v1/auth/authenticate", json=_payload())

        assert response.status_code == 200
        assert "token" in response.json()

    def test_sets_httponly_cookie(self, client):
        _create_user(client)
        response = client.post("/api/v1/auth/authenticate", json=_payload())

        cookie = response.cookies.get("access_token")
        assert cookie is not None
        assert "Bearer" in cookie

    def test_returns_400_with_wrong_password(self, client):
        _create_user(client)
        response = client.post(
            "/api/v1/auth/authenticate",
            json=_payload(password="SenhaErrada@123"),
        )

        assert response.status_code == 400

    def test_returns_400_with_unknown_email(self, client):
        _create_user(client)
        response = client.post(
            "/api/v1/auth/authenticate",
            json=_payload(email="naoexiste@example.com"),
        )

        assert response.status_code == 400


class TestGetMeRouter:
    def test_returns_200_with_user_data(self, client):
        _create_user(client)
        client.post("/api/v1/auth/authenticate", json=_payload())

        response = client.get("/api/v1/users/me")

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "joao@example.com"
        assert "name" in body
        assert "user_id" in body
        assert "is_active" in body

    def test_returns_401_without_cookie(self, client):
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401
