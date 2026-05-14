from pydantic import BaseModel, field_validator
from decimal import Decimal


class TransferRequest(BaseModel):
    origin_user_id: str          # viene del orchestrator (validado desde Redis)
    destination_phone: str       # teléfono del destinatario
    amount: Decimal
    trace_id: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        return v

    @field_validator("destination_phone")
    @classmethod
    def phone_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El teléfono destino es obligatorio")
        return v.strip()


class TransferResponse(BaseModel):
    transfer_id: str
    origin_account_id: str
    destination_account_id: str
    amount: Decimal
    status: str
    message: str


class ErrorResponse(BaseModel):
    error_code: str
    message: str
