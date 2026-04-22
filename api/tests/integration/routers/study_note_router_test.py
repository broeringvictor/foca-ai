from uuid import uuid8

from tests.factories.user import DEFAULT_PASSWORD


def _create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "first_name": "Joao",
            "last_name": "Silva",
            "email": "joao@example.com",
            "password": DEFAULT_PASSWORD,
            "password_confirm": DEFAULT_PASSWORD,
        },
    )
    assert response.status_code == 201


def _authenticate(client):
    response = client.post(
        "/api/v1/auth/authenticate",
        json={"email": "joao@example.com", "password": DEFAULT_PASSWORD},
    )
    assert response.status_code == 200


def _create_study_note(client, *, title: str = "Resumo de SQLAlchemy") -> str:
    response = client.post(
        "/api/v1/study-notes/",
        data={
            "title": title,
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
    return response.json()["study_note_id"]


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

    def test_list_and_get_study_note(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client, title="Resumo de Processo Civil")

        list_response = client.get("/api/v1/study-notes/")

        assert list_response.status_code == 200
        items = list_response.json()["items"]
        assert any(item["id"] == study_note_id for item in items)
        assert any(item["id"] == study_note_id and item["has_embedding"] is False for item in items)

        get_response = client.get(f"/api/v1/study-notes/{study_note_id}")

        assert get_response.status_code == 200
        body = get_response.json()
        assert body["id"] == study_note_id
        assert body["title"] == "Resumo de Processo Civil"
        assert "python" in body["tags"]
        assert body["questions"] == []

    def test_update_study_note(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client)

        response = client.patch(
            f"/api/v1/study-notes/{study_note_id}",
            data={
                "title": "Resumo atualizado",
                "description": "Descricao nova",
                "tags": "civil,processo",
            },
            files={
                "content_file": (
                    "updated.md",
                    "# Atualizado\n\nConteudo novo",
                    "text/markdown",
                )
            },
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Resumo atualizado"

        get_response = client.get(f"/api/v1/study-notes/{study_note_id}")
        assert get_response.status_code == 200
        updated = get_response.json()
        assert updated["title"] == "Resumo atualizado"
        assert updated["description"] == "Descricao nova"
        assert updated["content"].startswith("# Atualizado")
        assert updated["tags"] == ["civil", "processo"]

    def test_delete_study_note(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client)

        response = client.delete(f"/api/v1/study-notes/{study_note_id}")

        assert response.status_code == 200
        assert response.json()["study_note_id"] == study_note_id

        not_found_response = client.get(f"/api/v1/study-notes/{study_note_id}")
        assert not_found_response.status_code == 404

    def test_generate_embeddings_updates_list_flag(self, client, monkeypatch):
        class _FakeEmbeddings:
            def __init__(self):
                self.calls: list[str] = []

            async def aembed_query(self, text: str):
                self.calls.append(text)
                return [0.1] * 3072

        fake_embeddings = _FakeEmbeddings()
        monkeypatch.setattr(
            "app.api.dependecies.study_note.get_embedding_model",
            lambda: fake_embeddings,
        )

        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client, title="Resumo com embedding")

        response = client.post(f"/api/v1/study-notes/{study_note_id}/embeddings")

        assert response.status_code == 200
        body = response.json()
        assert body["study_note_id"] == study_note_id
        assert body["embedded"] is True
        assert len(fake_embeddings.calls) == 1
        assert "Resumo com embedding" in fake_embeddings.calls[0]

        list_response = client.get("/api/v1/study-notes/")
        assert list_response.status_code == 200
        assert any(
            item["id"] == study_note_id and item["has_embedding"] is True
            for item in list_response.json()["items"]
        )

    def test_get_study_note_returns_404_for_unknown_id(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.get(f"/api/v1/study-notes/{uuid8()}")

        assert response.status_code == 404

