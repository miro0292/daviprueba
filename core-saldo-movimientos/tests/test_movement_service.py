import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.movement_service import MovementService
from app.schemas.movement_schema import MovementsRequest
from app.models.account import Account
from app.models.movement import Movement

TRACE_ID = "trace-test-002"
USER_ID = "550e8400-e29b-41d4-a716-446655440000"
ACCOUNT_ID = "660e8400-e29b-41d4-a716-446655440001"


def make_mock_account():
    acc = MagicMock(spec=Account)
    acc.id = ACCOUNT_ID
    acc.status = "ACTIVA"
    return acc


def make_mock_movement(mov_type="DEBITO"):
    m = MagicMock(spec=Movement)
    m.id = "mov-uuid-1"
    m.transfer_id = "txn-uuid-1"
    m.type = mov_type
    m.amount = Decimal("50000.00")
    m.balance_after = Decimal("100000.00")
    m.created_at = datetime.now(timezone.utc)
    return m


class TestMovementService:
    @pytest.mark.asyncio
    async def test_get_movements_success(self):
        db = AsyncMock()
        service = MovementService(db)
        account = make_mock_account()
        movements = [make_mock_movement("DEBITO"), make_mock_movement("CREDITO")]

        with patch.object(service.repo, "find_active_by_user_id", return_value=account), \
             patch.object(service.repo, "count_movements", return_value=2), \
             patch.object(service.repo, "find_movements_paginated", return_value=movements):

            result = await service.get_movements(
                MovementsRequest(user_id=USER_ID, page=1, page_size=20), TRACE_ID
            )

        assert result.total == 2
        assert len(result.movements) == 2
        assert result.movements[0].type == "DEBITO"
        assert result.movements[1].type == "CREDITO"

    @pytest.mark.asyncio
    async def test_get_movements_account_not_found(self):
        db = AsyncMock()
        service = MovementService(db)

        with patch.object(service.repo, "find_active_by_user_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.get_movements(
                    MovementsRequest(user_id=USER_ID), TRACE_ID
                )

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_pagination_limits_page_size(self):
        db = AsyncMock()
        service = MovementService(db)
        account = make_mock_account()

        with patch.object(service.repo, "find_active_by_user_id", return_value=account), \
             patch.object(service.repo, "count_movements", return_value=0), \
             patch.object(service.repo, "find_movements_paginated", return_value=[]) as mock_paged:

            await service.get_movements(
                MovementsRequest(user_id=USER_ID, page=1, page_size=500), TRACE_ID
            )
            # page_size no puede superar 100
            _, call_kwargs = mock_paged.call_args
            assert mock_paged.call_args[0][2] <= 100

    @pytest.mark.asyncio
    async def test_empty_movements_returns_empty_list(self):
        db = AsyncMock()
        service = MovementService(db)
        account = make_mock_account()

        with patch.object(service.repo, "find_active_by_user_id", return_value=account), \
             patch.object(service.repo, "count_movements", return_value=0), \
             patch.object(service.repo, "find_movements_paginated", return_value=[]):

            result = await service.get_movements(
                MovementsRequest(user_id=USER_ID), TRACE_ID
            )

        assert result.total == 0
        assert result.movements == []
