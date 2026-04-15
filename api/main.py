from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.config.scalar_config import router as scalar_router
from app.api.errors.handlers import validation_error_handler, request_validation_error_handler
from app.infrastructure.config.settings import get_settings

get_settings()

app = FastAPI()
app.include_router(scalar_router)

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
