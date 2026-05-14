import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.movement_schema import MovementsRequest, MovementsResponse
from app.schemas.error_schema import ErrorResponse
from app.services.movement_service import MovementService
from app.utils.logger import logger

router = APIRouter(prefix="/core2", tags=["Movimientos"])


def get_trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id", "-")


@router.post(
    "/movements",
    response_model=MovementsResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Consulta de movimientos",
    description="Retorna los movimientos paginados de la cuenta asociada al user_id. Solo muestra movimientos del usuario autenticado.",
)
async def get_movements(
    body: MovementsRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    trace_id = get_trace_id(request)
    start = time.monotonic()
    result = await MovementService(db).get_movements(body, trace_id)
    logger.info("GET_MOVEMENTS", "Consulta completada", trace_id=trace_id,
                status="SUCCESS", duration_ms=int((time.monotonic() - start) * 1000))
    return result
