from tests.factories.user import DEFAULT_PASSWORD


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


def _authenticate(client):
    client.post(
        "/api/v1/auth/authenticate",
        json={"email": "joao@example.com", "password": DEFAULT_PASSWORD},
    )


class TestStudyNoteRouter:
    def test_create_study_note_returns_201(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.post(
            "/api/v1/study-notes/",
            data={
                "title": "Resumo de SQLAlchemy",
                "description": "Notas sobre sessao async",
                "tags": "python,fastapi,ddd",
            },
            files={
                "content_file": (
                    "note.md",
                    "# SQLAlchemy Async\n\n- Use AsyncSession",
                    "text/markdown",
                )
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert "study_note_id" in body
        assert body["title"] == "Resumo de SQLAlchemy"

    def test_create_study_note_returns_201_without_content_file(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.post(
            "/api/v1/study-notes/",
            data={
                "title": "Resumo sem arquivo",
                "description": "Nota criada sem markdown",
                "tags": "python,fastapi",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert "study_note_id" in body
        assert body["title"] == "Resumo sem arquivo"

    def test_create_study_note_rejects_invalid_extension(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.post(
            "/api/v1/study-notes/",
            data={"title": "Minha nota", "description": "Uma descricao"},
            files={"content_file": ("note.txt", "conteudo", "text/plain")},
        )

        assert response.status_code == 400

    def test_create_study_note_accepts_raw_html_content(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.post(
            "/api/v1/study-notes/",
            data={"title": "Minha nota", "description": "Uma descricao"},
            files={
                "content_file": (
                    "note.md",
                    "# Olha isso\n<script>alert('xss')</script>",
                    "text/markdown",
                )
            },
        )

        assert response.status_code == 201
