from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.api.config.scalar_config import router as scalar_router
from app.api.errors.exceptions import BadRequestError, ConflictError, NotFoundError
from app.api.errors.handlers import (
	validation_error_handler,
	request_validation_error_handler,
	value_error_handler,
	bad_request_error_handler,
	conflict_error_handler,
	not_found_error_handler,
)
from app.api.routers.v1 import api_router as v1_router
from app.infrastructure.config.settings import get_settings

get_settings()

app = FastAPI()
app.include_router(scalar_router)
app.include_router(v1_router, prefix="/api/v1")

app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(BadRequestError, bad_request_error_handler)
app.add_exception_handler(ConflictError, conflict_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
