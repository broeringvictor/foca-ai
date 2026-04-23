from uuid import uuid8
import pytest
from tests.factories.user import DEFAULT_PASSWORD
from app.domain.enums.law_area import LawArea

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


def _create_study_note(client, *, title: str = "Resumo de SQLAlchemy", area: str = "etica_profissional") -> str:
    response = client.post(
        "/api/v1/study-notes/",
        data={
            "area": area,
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
                "area": "direito_civil",
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
                "area": "direito_penal",
                "title": "Resumo sem arquivo",
                "description": "Nota criada sem markdown",
                "tags": "python,fastapi",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert "study_note_id" in body
        assert body["title"] == "Resumo sem arquivo"

    def test_submit_study_note_review(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client, area="direito_administrativo")
        
        payload = {
            "quality": 4 # GOOD
        }
        
        response = client.post(f"/api/v1/study-notes/{study_note_id}/review", json=payload)
        
        assert response.status_code == 200
        body = response.json()
        assert body["study_note_id"] == study_note_id
        assert body["new_progress"]["card_status"] == 2
        assert body["new_progress"]["interval_days"] == 3

    def test_list_due_study_notes(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client, title="Nota Vencida", area="direito_civil")
        
        # Como é nova, por padrão next_review_date = hoje, então deve estar no due
        response = client.get("/api/v1/study-notes/due")
        
        assert response.status_code == 200
        items = response.json()["items"]
        assert any(item["id"] == study_note_id for item in items)

    def test_create_study_note_rejects_invalid_extension(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.post(
            "/api/v1/study-notes/",
            data={"area": "direito_civil", "title": "Minha nota", "description": "Uma descricao"},
            files={"content_file": ("note.txt", "conteudo", "text/plain")},
        )

        assert response.status_code == 400

    def test_list_and_get_study_note(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client, title="Resumo de Processo Civil")

        list_response = client.get("/api/v1/study-notes/")

        assert list_response.status_code == 200
        items = list_response.json()["items"]
        assert any(item["id"] == study_note_id for item in items)

        get_response = client.get(f"/api/v1/study-notes/{study_note_id}")

        assert get_response.status_code == 200
        body = get_response.json()
        assert body["id"] == study_note_id
        assert body["title"] == "Resumo de Processo Civil"

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
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Resumo atualizado"

    def test_delete_study_note(self, client):
        _create_user(client)
        _authenticate(client)
        study_note_id = _create_study_note(client)

        response = client.delete(f"/api/v1/study-notes/{study_note_id}")

        assert response.status_code == 200
        assert response.json()["study_note_id"] == study_note_id

    def test_get_study_note_returns_404_for_unknown_id(self, client):
        _create_user(client)
        _authenticate(client)

        response = client.get(f"/api/v1/study-notes/{uuid8()}")

        assert response.status_code == 404
