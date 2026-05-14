from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.transfer_repository import TransferRepository
from app.models.transfer import Transfer
from app.models.movement import Movement
from app.schemas.transfer_schema import TransferRequest, TransferResponse
from app.utils.logger import logger


class TransferService:
    def __init__(self, db: AsyncSession):
        self.repo = TransferRepository(db)
        self.db = db

    async def execute(self, data: TransferRequest, trace_id: str) -> TransferResponse:
        # ── 1. Validar usuario origen ──────────────────────────────────────────
        origin_user = await self.repo.find_user_by_id(data.origin_user_id)
        if not origin_user:
            self._fail("ORIGIN_USER_NOT_FOUND", "Usuario origen no encontrado", 404, trace_id)
        if origin_user.status != "ACTIVA":
            self._fail("ORIGIN_USER_INACTIVE", "Usuario origen inACTIVA o bloqueado", 422, trace_id)

        # ── 2. Validar cuenta origen ───────────────────────────────────────────
        origin_account = await self.repo.find_active_account_by_user_id(data.origin_user_id)
        if not origin_account:
            self._fail("ORIGIN_ACCOUNT_NOT_FOUND", "Cuenta origen no encontrada o inactiva", 404, trace_id)

        # ── 3. Validar usuario destino por teléfono ────────────────────────────
        dest_user = await self.repo.find_user_by_phone(data.destination_phone)
        if not dest_user:
            self._fail("DEST_USER_NOT_FOUND", "No existe usuario con ese número de teléfono", 404, trace_id)
        if dest_user.status != "ACTIVA":
            self._fail("DEST_USER_INACTIVE", "Usuario destino inACTIVA o bloqueado", 422, trace_id)

        # ── 4. Validar cuenta destino ──────────────────────────────────────────
        dest_account = await self.repo.find_active_account_by_user_id(str(dest_user.id))
        if not dest_account:
            self._fail("DEST_ACCOUNT_NOT_FOUND", "Cuenta destino no encontrada o inactiva", 404, trace_id)

        # ── 5. Validar que no sea auto-transferencia ───────────────────────────
        if str(origin_user.id) == str(dest_user.id):
            self._fail("SELF_TRANSFER", "No puedes transferir a tu propia cuenta", 422, trace_id)

        # ── 6. Validar monto contra saldo disponible ───────────────────────────
        if data.amount > origin_account.balance:
            self._fail("INSUFFICIENT_FUNDS", "Saldo insuficiente para realizar la transferencia", 422, trace_id)

        # ── 7. Ejecutar transacción atómica ────────────────────────────────────
        try:
            result = await self._execute_transaction(
                origin_account.id,
                dest_account.id,
                data.amount,
                trace_id,
            )
            await self.db.commit()
            logger.info("TRANSFER", "Transferencia ejecutada exitosamente",
                        trace_id=trace_id, status="SUCCESS", http_status=201)
            return result
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error("TRANSFER", f"Error inesperado en transacción: {str(e)}",
                         trace_id=trace_id, status="FAILED", http_status=500,
                         error_code="TRANSACTION_ERROR")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error_code": "TRANSACTION_ERROR", "message": "Error al ejecutar la transferencia"},
            )

    async def _execute_transaction(
        self,
        origin_account_id,
        dest_account_id,
        amount: Decimal,
        trace_id: str,
    ) -> TransferResponse:
        # Bloqueo pesimista: evita condiciones de carrera con transacciones concurrentes
        origin = await self.repo.find_account_for_update(origin_account_id)
        dest = await self.repo.find_account_for_update(dest_account_id)

        # Re-validar saldo con bloqueo (otra transacción pudo haber modificado el saldo)
        if amount > origin.balance:
            self._fail("INSUFFICIENT_FUNDS", "Saldo insuficiente (verificación bajo bloqueo)", 422, trace_id)

        # Actualizar saldos
        origin.balance = origin.balance - amount
        dest.balance = dest.balance + amount

        # Registrar transferencia
        transfer = Transfer(
            origin_account_id=origin_account_id,
            destination_account_id=dest_account_id,
            amount=amount,
            status="COMPLETADA",
            trace_id=trace_id,
        )
        transfer = await self.repo.save_transfer(transfer)

        # Registrar movimiento DEBITO para origen
        await self.repo.save_movement(Movement(
            account_id=origin_account_id,
            transfer_id=transfer.id,
            type="DEBITO",
            amount=amount,
            balance_after=origin.balance,
        ))

        # Registrar movimiento CREDITO para destino
        await self.repo.save_movement(Movement(
            account_id=dest_account_id,
            transfer_id=transfer.id,
            type="CREDITO",
            amount=amount,
            balance_after=dest.balance,
        ))

        return TransferResponse(
            transfer_id=str(transfer.id),
            origin_account_id=str(origin_account_id),
            destination_account_id=str(dest_account_id),
            amount=amount,
            status="COMPLETADA",
            message="Transferencia realizada exitosamente",
        )

    def _fail(self, error_code: str, message: str, http_status: int, trace_id: str):
        logger.warning("TRANSFER", message,
                       trace_id=trace_id, status="FAILED",
                       http_status=http_status, error_code=error_code)
        raise HTTPException(
            status_code=http_status,
            detail={"error_code": error_code, "message": message},
        )
