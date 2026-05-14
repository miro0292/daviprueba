from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routers.transfer_router import router
from app.utils.logger import logger

app = FastAPI(
    title="Core Transferencias",
    description="Servicio de ejecución de transferencias entre cuentas",
    version="1.0.0",
    docs_url="/core3/docs",
    openapi_url="/core3/openapi.json",
)

app.include_router(router)


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


@app.get("/core3/health", tags=["Health"])
async def health():
    return {"status": "UP", "service": "core-transferencias"}
