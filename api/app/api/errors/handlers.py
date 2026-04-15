from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from typing import cast

from app.api.errors.formatters import format_errors

async def validation_error_handler(
    request: Request, exc: Exception
) -> Response:
    err = cast(ValidationError, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": format_errors(err.errors())},
    )


async def request_validation_error_handler(
    request: Request, exc: Exception
) -> Response:
    err = cast(RequestValidationError, exc)
    return JSONResponse(
        status_code=422,
        content=dict(detail=format_errors(err.errors())),
    )
