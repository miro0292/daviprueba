from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.account_repository import AccountRepository
from app.schemas.balance_schema import BalanceRequest, BalanceResponse
from app.utils.logger import logger


class BalanceService:
    def __init__(self, db: AsyncSession):
        self.repo = AccountRepository(db)

    async def get_balance(self, data: BalanceRequest, trace_id: str) -> BalanceResponse:
        account = await self.repo.find_active_by_user_id(data.user_id)

        if not account:
            logger.warning("GET_BALANCE", "Cuenta activa no encontrada",
                           trace_id=trace_id, status="FAILED", http_status=404,
                           error_code="ACCOUNT_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": "ACCOUNT_NOT_FOUND", "message": "Cuenta no encontrada o inactiva"},
            )

        logger.info("GET_BALANCE", "Saldo consultado",
                    trace_id=trace_id, status="SUCCESS", http_status=200)

        return BalanceResponse(
            user_id=data.user_id,
            account_id=str(account.id),
            balance=account.balance,
            account_status=account.status,
        )
