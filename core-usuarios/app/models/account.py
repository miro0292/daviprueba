import uuid
from sqlalchemy import Column, Numeric, String, Enum, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import enum


class AccountStatus(str, enum.Enum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    status = Column(Enum(AccountStatus, native_enum=False), default=AccountStatus.ACTIVA, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
