import time
import uuid
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user_schema import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.schemas.error_schema import ErrorResponse
from app.services.user_service import UserService
from app.utils.logger import logger

router = APIRouter(prefix="/core1", tags=["Usuarios"])


def get_trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id", str(uuid.uuid4()))


@router.post(
    "/users/register",
    response_model=RegisterResponse,
    status_code=201,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Registro de usuario",
)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    trace_id = get_trace_id(request)
    start = time.monotonic()
    service = UserService(db)
    result = await service.register(body, trace_id)
    logger.info("REGISTER", "Registro completado", trace_id=trace_id,
                status="SUCCESS", duration_ms=int((time.monotonic() - start) * 1000))
    return result


@router.post(
    "/users/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}},
    summary="Validación de credenciales",
)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    trace_id = get_trace_id(request)
    start = time.monotonic()
    service = UserService(db)
    result = await service.login(body, trace_id)
    logger.info("LOGIN", "Login completado", trace_id=trace_id,
                status="SUCCESS", duration_ms=int((time.monotonic() - start) * 1000))
    return result
