import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from fastapi import HTTPException
from app.services.balance_service import BalanceService
from app.schemas.balance_schema import BalanceRequest
from app.models.account import Account

TRACE_ID = "trace-test-001"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"


def make_mock_account(**kwargs):
    acc = MagicMock(spec=Account)
    acc.id = "acc-uuid-1"
    acc.user_id = USER_ID
    acc.balance = Decimal("150000.00")
    acc.status = "ACTIVA"
    for k, v in kwargs.items():
        setattr(acc, k, v)
    return acc


class TestBalanceService:
    @pytest.mark.asyncio
    async def test_get_balance_success(self):
        db = AsyncMock()
        service = BalanceService(db)
        account = make_mock_account()

        with patch.object(service.repo, "find_active_by_user_id", return_value=account):
            result = await service.get_balance(BalanceRequest(user_id=USER_ID), TRACE_ID)

        assert result.balance == Decimal("150000.00")
        assert result.user_id == USER_ID
        assert result.account_status == "ACTIVA"

    @pytest.mark.asyncio
    async def test_get_balance_account_not_found(self):
        db = AsyncMock()
        service = BalanceService(db)

        with patch.object(service.repo, "find_active_by_user_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.get_balance(BalanceRequest(user_id=USER_ID), TRACE_ID)

        assert exc.value.status_code == 404
        assert exc.value.detail["error_code"] == "ACCOUNT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_balance_is_never_negative(self):
        db = AsyncMock()
        service = BalanceService(db)
        account = make_mock_account(balance=Decimal("0.00"))

        with patch.object(service.repo, "find_active_by_user_id", return_value=account):
            result = await service.get_balance(BalanceRequest(user_id=USER_ID), TRACE_ID)

        assert result.balance >= Decimal("0.00")
