import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from fastapi import HTTPException
from app.services.transfer_service import TransferService
from app.schemas.transfer_schema import TransferRequest
from app.models.user import User
from app.models.account import Account
from app.models.transfer import Transfer

TRACE_ID = "trace-transfer-001"
ORIGIN_USER_ID = str(uuid.uuid4())
DEST_USER_ID = str(uuid.uuid4())
ORIGIN_ACC_ID = uuid.uuid4()
DEST_ACC_ID = uuid.uuid4()
DEST_PHONE = "3009876543"


def make_user(user_id: str, status: str = "ACTIVA", phone: str = "3001111111") -> MagicMock:
    u = MagicMock(spec=User)
    u.id = uuid.UUID(user_id)
    u.status = status
    u.phone = phone
    return u


def make_account(acc_id: uuid.UUID, user_id: str, balance: Decimal = Decimal("500000.00")) -> MagicMock:
    a = MagicMock(spec=Account)
    a.id = acc_id
    a.user_id = uuid.UUID(user_id)
    a.balance = balance
    a.status = "ACTIVA"
    return a


def make_transfer_request(amount: Decimal = Decimal("100000.00")) -> TransferRequest:
    return TransferRequest(
        origin_user_id=ORIGIN_USER_ID,
        destination_phone=DEST_PHONE,
        amount=amount,
    )


def make_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


class TestTransferValidations:
    @pytest.mark.asyncio
    async def test_origin_user_not_found(self):
        db = make_db()
        service = TransferService(db)
        with patch.object(service.repo, "find_user_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)
        assert exc.value.status_code == 404
        assert exc.value.detail["error_code"] == "ORIGIN_USER_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_origin_user_blocked(self):
        db = make_db()
        service = TransferService(db)
        with patch.object(service.repo, "find_user_by_id", return_value=make_user(ORIGIN_USER_ID, "BLOQUEADO")):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)
        assert exc.value.status_code == 422
        assert exc.value.detail["error_code"] == "ORIGIN_USER_INACTIVE"

    @pytest.mark.asyncio
    async def test_origin_account_not_found(self):
        db = make_db()
        service = TransferService(db)
        with patch.object(service.repo, "find_user_by_id", return_value=make_user(ORIGIN_USER_ID)), \
             patch.object(service.repo, "find_active_account_by_user_id", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)
        assert exc.value.detail["error_code"] == "ORIGIN_ACCOUNT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_destination_user_not_found(self):
        db = make_db()
        service = TransferService(db)
        origin_acc = make_account(ORIGIN_ACC_ID, ORIGIN_USER_ID)

        with patch.object(service.repo, "find_user_by_id", return_value=make_user(ORIGIN_USER_ID)), \
             patch.object(service.repo, "find_active_account_by_user_id", return_value=origin_acc), \
             patch.object(service.repo, "find_user_by_phone", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)
        assert exc.value.detail["error_code"] == "DEST_USER_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_self_transfer_rejected(self):
        db = make_db()
        service = TransferService(db)
        same_user = make_user(ORIGIN_USER_ID, phone=DEST_PHONE)
        origin_acc = make_account(ORIGIN_ACC_ID, ORIGIN_USER_ID)
        dest_acc = make_account(DEST_ACC_ID, ORIGIN_USER_ID)

        with patch.object(service.repo, "find_user_by_id", return_value=same_user), \
             patch.object(service.repo, "find_active_account_by_user_id", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "find_user_by_phone", return_value=same_user):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)
        assert exc.value.detail["error_code"] == "SELF_TRANSFER"

    @pytest.mark.asyncio
    async def test_insufficient_funds(self):
        db = make_db()
        service = TransferService(db)
        origin_acc = make_account(ORIGIN_ACC_ID, ORIGIN_USER_ID, balance=Decimal("50.00"))
        dest_acc = make_account(DEST_ACC_ID, DEST_USER_ID)
        dest_user = make_user(DEST_USER_ID, phone=DEST_PHONE)

        with patch.object(service.repo, "find_user_by_id", return_value=make_user(ORIGIN_USER_ID)), \
             patch.object(service.repo, "find_active_account_by_user_id", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "find_user_by_phone", return_value=dest_user):
            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(Decimal("100000.00")), TRACE_ID)
        assert exc.value.detail["error_code"] == "INSUFFICIENT_FUNDS"

    @pytest.mark.asyncio
    async def test_amount_must_be_positive(self):
        with pytest.raises(Exception):
            TransferRequest(origin_user_id=ORIGIN_USER_ID, destination_phone=DEST_PHONE, amount=Decimal("0"))

    @pytest.mark.asyncio
    async def test_amount_negative_rejected(self):
        with pytest.raises(Exception):
            TransferRequest(origin_user_id=ORIGIN_USER_ID, destination_phone=DEST_PHONE, amount=Decimal("-100"))


class TestTransferSuccess:
    @pytest.mark.asyncio
    async def test_successful_transfer_updates_balances(self):
        db = make_db()
        service = TransferService(db)

        origin_user = make_user(ORIGIN_USER_ID)
        dest_user = make_user(DEST_USER_ID, phone=DEST_PHONE)
        origin_acc = make_account(ORIGIN_ACC_ID, ORIGIN_USER_ID, balance=Decimal("500000.00"))
        dest_acc = make_account(DEST_ACC_ID, DEST_USER_ID, balance=Decimal("100000.00"))

        mock_transfer = MagicMock(spec=Transfer)
        mock_transfer.id = uuid.uuid4()

        with patch.object(service.repo, "find_user_by_id", return_value=origin_user), \
             patch.object(service.repo, "find_active_account_by_user_id", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "find_user_by_phone", return_value=dest_user), \
             patch.object(service.repo, "find_account_for_update", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "save_transfer", return_value=mock_transfer), \
             patch.object(service.repo, "save_movement", return_value=None):

            result = await service.execute(make_transfer_request(Decimal("100000.00")), TRACE_ID)

        assert result.status == "COMPLETADA"
        assert origin_acc.balance == Decimal("400000.00")
        assert dest_acc.balance == Decimal("200000.00")
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback_on_error(self):
        db = make_db()
        service = TransferService(db)

        origin_user = make_user(ORIGIN_USER_ID)
        dest_user = make_user(DEST_USER_ID, phone=DEST_PHONE)
        origin_acc = make_account(ORIGIN_ACC_ID, ORIGIN_USER_ID)
        dest_acc = make_account(DEST_ACC_ID, DEST_USER_ID)

        with patch.object(service.repo, "find_user_by_id", return_value=origin_user), \
             patch.object(service.repo, "find_active_account_by_user_id", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "find_user_by_phone", return_value=dest_user), \
             patch.object(service.repo, "find_account_for_update", side_effect=[origin_acc, dest_acc]), \
             patch.object(service.repo, "save_transfer", side_effect=Exception("DB error")):

            with pytest.raises(HTTPException) as exc:
                await service.execute(make_transfer_request(), TRACE_ID)

        db.rollback.assert_called_once()
        assert exc.value.status_code == 500
