from fastapi import APIRouter, status, Depends

from app.api.dependecies.user import get_create_user_dependency
from app.application.dto.user.create_dto import CreateUserOutput, CreateUserInput
from app.application.use_cases.user.create import CreateUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=CreateUserOutput, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserInput,
    use_case: CreateUser = Depends(get_create_user_dependency),
) -> CreateUserOutput:
    return await use_case.execute(body)