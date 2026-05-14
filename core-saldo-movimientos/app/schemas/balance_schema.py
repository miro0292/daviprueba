from pydantic import BaseModel
from decimal import Decimal


class BalanceRequest(BaseModel):
    user_id: str


class BalanceResponse(BaseModel):
    user_id: str
    account_id: str
    balance: Decimal
    currency: str = "COP"
    account_status: str
