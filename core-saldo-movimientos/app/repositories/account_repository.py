from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.account import Account
from app.models.movement import Movement
import uuid


class AccountRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_active_by_user_id(self, user_id: str) -> Account | None:
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == uuid.UUID(user_id),
                Account.status == "ACTIVA",
            )
        )
        return result.scalar_one_or_none()

    async def count_movements(self, account_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count()).where(Movement.account_id == account_id)
        )
        return result.scalar_one()

    async def find_movements_paginated(
        self, account_id: uuid.UUID, offset: int, limit: int
    ) -> list[Movement]:
        result = await self.db.execute(
            select(Movement)
            .where(Movement.account_id == account_id)
            .order_by(Movement.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())
