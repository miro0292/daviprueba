import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.account import Account
from app.models.transfer import Transfer
from app.models.movement import Movement


class TransferRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_user_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        return result.scalar_one_or_none()

    async def find_user_by_phone(self, phone: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def find_active_account_by_user_id(self, user_id: str) -> Account | None:
        result = await self.db.execute(
            select(Account).where(
                Account.user_id == uuid.UUID(user_id),
                Account.status == "ACTIVA",
            )
        )
        return result.scalar_one_or_none()

    # Bloqueo pesimista para evitar condiciones de carrera en la transacción
    async def find_account_for_update(self, account_id: uuid.UUID) -> Account | None:
        result = await self.db.execute(
            select(Account)
            .where(Account.id == account_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def save_transfer(self, transfer: Transfer) -> Transfer:
        self.db.add(transfer)
        await self.db.flush()
        await self.db.refresh(transfer)
        return transfer

    async def save_movement(self, movement: Movement) -> None:
        self.db.add(movement)
        await self.db.flush()
