from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


class MovementsRequest(BaseModel):
    user_id: str
    page: Optional[int] = 1
    page_size: Optional[int] = 20


class MovementItem(BaseModel):
    id: str
    transfer_id: str
    type: str           # DEBITO | CREDITO
    amount: Decimal
    balance_after: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class MovementsResponse(BaseModel):
    user_id: str
    account_id: str
    total: int
    page: int
    page_size: int
    movements: List[MovementItem]
