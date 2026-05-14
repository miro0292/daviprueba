from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers.balance_router import router as balance_router
from app.routers.movement_router import router as movement_router
from app.utils.logger import logger

app = FastAPI(
    title="Core Saldo y Movimientos",
    description="Servicio de consulta de saldo y movimientos de cuentas",
    version="1.0.0",
    docs_url="/core2/docs",
    openapi_url="/core2/openapi.json",
)

app.include_router(balance_router)
app.include_router(movement_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [{"field": e["loc"][-1], "message": e["msg"]} for e in exc.errors()]
    logger.warning("VALIDATION", "Error de validación en request",
                   http_status=422, error_code="VALIDATION_ERROR")
    return JSONResponse(status_code=422, content={
        "error_code": "VALIDATION_ERROR",
        "message": "Datos de entrada inválidos",
        "detail": errors,
    })


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error("UNHANDLED", "Error inesperado",
                 http_status=500, error_code="INTERNAL_ERROR")
    return JSONResponse(status_code=500, content={
        "error_code": "INTERNAL_ERROR",
        "message": "Error interno del servidor",
    })


@app.get("/core2/health", tags=["Health"])
async def health():
    return {"status": "UP", "service": "core-saldo-movimientos"}
