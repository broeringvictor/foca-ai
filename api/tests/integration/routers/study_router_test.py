import pytest
from uuid import uuid8
from app.api.dependecies.auth import get_current_user_id
from app.domain.enums.law_area import LawArea
from app.domain.enums.alternatives import Alternative
from app.infrastructure.session import get_session
from main import app
from tests.factories.question import QuestionFactory

@pytest.fixture
def auth_user(user_on_db):
    app.dependency_overrides[get_current_user_id] = lambda: user_on_db.id
    yield user_on_db
    app.dependency_overrides.pop(get_current_user_id, None)

@pytest.fixture
def session_override(session):
    async def _get_session():
        yield session
    
    app.dependency_overrides[get_session] = _get_session
    yield session
    app.dependency_overrides.pop(get_session, None)


@pytest.mark.asyncio
async def test_list_study_progress(client, auth_user, session_override):
    # Criar uma questão para garantir que venha na lista
    question_model = QuestionFactory.create(
        area=LawArea.CIVIL,
        embedding=[0.1] * 3072
    )
    session_override.add(question_model)
    await session_override.commit()

    response = client.get("/api/v1/study/progress")
    
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert len(body["items"]) == len(LawArea)
    
    # Verificar se a área Civil tem a questão
    civil_item = next(item for item in body["items"] if item["area"] == LawArea.CIVIL.value)
    assert len(civil_item["questions"]) > 0
    assert civil_item["questions"][0]["id"] == str(question_model.id)


@pytest.mark.asyncio
async def test_submit_area_review_through_question(client, auth_user, session_override):
    # 1. Criar uma questão no banco
    question_model = QuestionFactory.create(area=LawArea.CIVIL, correct=Alternative.A)
    session_override.add(question_model)
    await session_override.commit()
    await session_override.refresh(question_model)
    
    # 2. Submeter review
    payload = {
        "question_id": str(question_model.id),
        "response": "A",
        "quality": 4 # GOOD
    }
    
    response = client.post("/api/v1/study/review", json=payload)
    
    assert response.status_code == 200
    body = response.json()
    assert body["area"] == LawArea.CIVIL.value
    assert body["is_correct"] is True
    assert body["new_progress"]["card_status"] == 2

@pytest.mark.asyncio
async def test_submit_wrong_answer_review(client, auth_user, session_override):
    question_model = QuestionFactory.create(area=LawArea.TAX, correct=Alternative.B)
    session_override.add(question_model)
    await session_override.commit()
    await session_override.refresh(question_model)

    payload = {
        "question_id": str(question_model.id),
        "response": "A", # Errada
        "quality": 5 # EASY (Sistema deve ignorar e forçar AGAIN/0)
    }

    response = client.post("/api/v1/study/review", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["is_correct"] is False
    assert body["correct_alternative"] == "B"
    # Mesmo enviando qualidade 5, o status deve ser 1 (LEARNING) e intervalo 1
    assert body["new_progress"]["card_status"] == 1 
    assert body["new_progress"]["interval_days"] == 1



@pytest.mark.asyncio
async def test_list_due_study_areas(client, auth_user, session_override):
    from app.infrastructure.model.study_model import StudyModel
    from datetime import datetime, timezone
    
    # Criar um registro de estudo que já venceu
    study_model = StudyModel(
        id=uuid8(),
        user_id=auth_user.id,
        area=LawArea.CRIMINAL.value,
        review_progress={
            "ease_factor": 2.5,
            "interval_days": 1,
            "next_review_date": datetime.now(timezone.utc).date().isoformat(),
            "card_status": 2,
            "lapsed_count": 0,
        },
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    session_override.add(study_model)
    
    # Criar uma questão com embedding para a área criminal
    question = QuestionFactory.create(
        area=LawArea.CRIMINAL,
        embedding=[0.1] * 3072
    )
    session_override.add(question)
    
    await session_override.commit()
    
    response = client.get("/api/v1/study/due")
    assert response.status_code == 200
    body = response.json()
    
    areas = [item["area"] for item in body["items"]]
    assert LawArea.CRIMINAL.value in areas
