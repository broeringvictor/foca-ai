from uuid import UUID
from fastapi import APIRouter, Depends, status

from app.api.dependecies.auth import get_current_user_id
from app.api.dependecies.study import (
    get_list_due_law_areas_dependency,
    get_list_user_study_progress_dependency,
    get_submit_area_review_dependency,
    get_next_study_session_dependency
)
from app.application.dto.study.study_dto import (
    ListStudyProgressResponse,
    SubmitAreaReviewDTO,
    SubmitAreaReviewResponse
)
from app.application.use_cases.study.list_due import ListDueLawAreas
from app.application.use_cases.study.list_progress import ListUserStudyProgress
from app.application.use_cases.study.submit_review import SubmitAreaReview
from app.application.use_cases.study.get_next_session import GetNextStudySession

router = APIRouter(
    prefix="/study",
    tags=["study"],
)

@router.get(
    "/session",
    summary="get next study session",
    description="Retorna as próximas 10 questões ideais para o usuário estudar (priorizando revisões vencidas do SM-2).",
    response_model=ListStudyProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def get_session_questions(
    limit: int = 10,
    user_id: UUID = Depends(get_current_user_id),
    use_case: GetNextStudySession = Depends(get_next_study_session_dependency),
) -> ListStudyProgressResponse:
    return await use_case.execute(user_id, limit=limit)

@router.get(
    "/due",
    summary="list due areas",
    description="Lista as áreas do Direito que estão vencidas para revisão (SM-2) para o usuário.",
    response_model=ListStudyProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def list_due(
    user_id: UUID = Depends(get_current_user_id),
    use_case: ListDueLawAreas = Depends(get_list_due_law_areas_dependency),
) -> ListStudyProgressResponse:
    return await use_case.execute(user_id)

@router.get(
    "/progress",
    summary="list area progress",
    description="Lista o progresso de estudo em cada área do Direito para o usuário.",
    response_model=ListStudyProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def list_progress(
    user_id: UUID = Depends(get_current_user_id),
    use_case: ListUserStudyProgress = Depends(get_list_user_study_progress_dependency),
) -> ListStudyProgressResponse:
    return await use_case.execute(user_id)

@router.post(
    "/review",
    summary="submit area review",
    description=(
        "Registra uma revisão para uma área específica do Direito com base em uma questão.\n\n"
        "**Valores de Qualidade (SM-2):**\n"
        "- `0`: **AGAIN** - Errou ou esqueceu (vencimento em 1 dia, penalidade no Ease Factor).\n"
        "- `3`: **HARD** - Acertou com dificuldade.\n"
        "- `4`: **GOOD** - Acertou com esforço normal.\n"
        "- `5`: **EASY** - Acertou com facilidade.\n\n"
        "**Importante:** O sistema valida a resposta (`response`). Se o usuário errar a questão, "
        "o algoritmo forçará automaticamente a qualidade para `0` (AGAIN), ignorando o valor enviado."
    ),
    response_model=SubmitAreaReviewResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_review(
    dto: SubmitAreaReviewDTO,
    user_id: UUID = Depends(get_current_user_id),
    use_case: SubmitAreaReview = Depends(get_submit_area_review_dependency),
) -> SubmitAreaReviewResponse:
    return await use_case.execute(user_id, dto)
