# Configuração do scalar, interface supeior ao do swagger
# preferença pessoal.

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

router = APIRouter()


@router.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/scalar")


@router.get("/scalar", include_in_schema=False)
async def scalar():
    return get_scalar_api_reference(
        openapi_url="/openapi.json",
        # Avoid CORS issues
        scalar_proxy_url="https://proxy.scalar.com",
    )
