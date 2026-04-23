from fastapi import APIRouter

from .auth_router import router as auth_router
from .exam_router import router as exam_router
from .question_router import router as question_router
from .study_note_router import router as study_note_router
from .study_router import router as study_router
from .user_router import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(study_note_router)
api_router.include_router(study_router)
api_router.include_router(exam_router)
api_router.include_router(question_router)

__all__ = ["api_router"]
