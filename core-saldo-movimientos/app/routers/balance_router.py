import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.balance_schema import BalanceRequest, BalanceResponse
from app.schemas.error_schema import ErrorResponse
from app.services.balance_service import BalanceService
from app.utils.logger import logger

router = APIRouter(prefix="/core2", tags=["Saldo"])


def get_trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id", "-")


@router.post(
    "/balance",
    response_model=BalanceResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Consulta de saldo",
    description="Retorna el saldo de la cuenta asociada al user_id. El user_id siempre proviene del orchestrator (validado desde Redis), nunca del frontend.",
)
async def get_balance(
    body: BalanceRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    trace_id = get_trace_id(request)
    start = time.monotonic()
    result = await BalanceService(db).get_balance(body, trace_id)
    logger.info("GET_BALANCE", "Consulta completada", trace_id=trace_id,
                status="SUCCESS", duration_ms=int((time.monotonic() - start) * 1000))
    return result
