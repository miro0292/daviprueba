import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.transfer_schema import TransferRequest, TransferResponse, ErrorResponse
from app.services.transfer_service import TransferService
from app.utils.logger import logger

router = APIRouter(prefix="/core3", tags=["Transferencias"])


def get_trace_id(request: Request) -> str:
    return request.headers.get("X-Trace-Id", "-")


@router.post(
    "/transfers",
    response_model=TransferResponse,
    status_code=201,
    responses={
        404: {"model": ErrorResponse, "description": "Usuario o cuenta no encontrada"},
        422: {"model": ErrorResponse, "description": "Validación de negocio fallida"},
        500: {"model": ErrorResponse, "description": "Error en transacción"},
    },
    summary="Ejecutar transferencia",
    description="""
Ejecuta una transferencia entre cuentas de forma atómica.

**Validaciones aplicadas:**
- Usuario origen y destino deben existir y estar ACTIVAS
- Ambas cuentas deben estar ACTIVAS
- No se permite auto-transferencia
- Monto debe ser mayor a cero
- Monto no puede superar el saldo disponible

**Genera:** 1 registro de transferencia + 1 movimiento DEBITO + 1 movimiento CREDITO.

Si cualquier paso falla, toda la operación hace **rollback** automático.
    """,
)
async def execute_transfer(
    body: TransferRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    trace_id = get_trace_id(request)
    body.trace_id = trace_id
    start = time.monotonic()
    result = await TransferService(db).execute(body, trace_id)
    logger.info("TRANSFER", "Request completado", trace_id=trace_id,
                status="SUCCESS", duration_ms=int((time.monotonic() - start) * 1000))
    return result
