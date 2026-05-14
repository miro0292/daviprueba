from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.account_repository import AccountRepository
from app.schemas.movement_schema import MovementsRequest, MovementsResponse, MovementItem
from app.utils.logger import logger


class MovementService:
    def __init__(self, db: AsyncSession):
        self.repo = AccountRepository(db)

    async def get_movements(self, data: MovementsRequest, trace_id: str) -> MovementsResponse:
        account = await self.repo.find_active_by_user_id(data.user_id)

        if not account:
            logger.warning("GET_MOVEMENTS", "Cuenta activa no encontrada",
                           trace_id=trace_id, status="FAILED", http_status=404,
                           error_code="ACCOUNT_NOT_FOUND")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error_code": "ACCOUNT_NOT_FOUND", "message": "Cuenta no encontrada o inactiva"},
            )

        page = max(1, data.page or 1)
        page_size = min(100, max(1, data.page_size or 20))
        offset = (page - 1) * page_size

        total = await self.repo.count_movements(account.id)
        movements = await self.repo.find_movements_paginated(account.id, offset, page_size)

        logger.info("GET_MOVEMENTS", f"Movimientos consultados: {len(movements)}",
                    trace_id=trace_id, status="SUCCESS", http_status=200)

        return MovementsResponse(
            user_id=data.user_id,
            account_id=str(account.id),
            total=total,
            page=page,
            page_size=page_size,
            movements=[
                MovementItem(
                    id=str(m.id),
                    transfer_id=str(m.transfer_id),
                    type=m.type,
                    amount=m.amount,
                    balance_after=m.balance_after,
                    created_at=m.created_at,
                )
                for m in movements
            ],
        )
