import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.user_service import UserService
from app.schemas.user_schema import RegisterRequest, LoginRequest
from app.models.user import User, UserStatus
from app.utils.password import hash_password

TRACE_ID = "test-trace-123"


def make_mock_db():
    db = AsyncMock()
    db.commit = AsyncMock()
    return db


def make_register_request(**overrides):
    data = {
        "document_number": "12345678",
        "email": "test@test.com",
        "phone": "3001234567",
        "username": "testuser",
        "password": "Secure1234",
    }
    data.update(overrides)
    return RegisterRequest(**data)


class TestRegister:
    @pytest.mark.asyncio
    async def test_register_success(self):
        db = make_mock_db()
        service = UserService(db)

        with patch.object(service.repo, "find_by_document", return_value=None), \
             patch.object(service.repo, "find_by_email", return_value=None), \
             patch.object(service.repo, "find_by_phone", return_value=None), \
             patch.object(service.repo, "find_by_username", return_value=None), \
             patch.object(service.repo, "create", new_callable=AsyncMock) as mock_create, \
             patch.object(service.repo, "create_account", new_callable=AsyncMock):

            mock_user = MagicMock(spec=User)
            mock_user.id = "uuid-1"
            mock_user.username = "testuser"
            mock_user.email = "test@test.com"
            mock_user.status = UserStatus.ACTIVA
            mock_create.return_value = mock_user

            result = await service.register(make_register_request(), TRACE_ID)

            assert result.username == "testuser"
            assert result.status == "ACTIVA"

    @pytest.mark.asyncio
    async def test_register_duplicate_document(self):
        db = make_mock_db()
        service = UserService(db)
        existing = MagicMock(spec=User)

        with patch.object(service.repo, "find_by_document", return_value=existing):
            with pytest.raises(HTTPException) as exc:
                await service.register(make_register_request(), TRACE_ID)
            assert exc.value.status_code == 409
            assert exc.value.detail["error_code"] == "DOCUMENT_EXISTS"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        db = make_mock_db()
        service = UserService(db)
        existing = MagicMock(spec=User)

        with patch.object(service.repo, "find_by_document", return_value=None), \
             patch.object(service.repo, "find_by_email", return_value=existing):
            with pytest.raises(HTTPException) as exc:
                await service.register(make_register_request(), TRACE_ID)
            assert exc.value.status_code == 409
            assert exc.value.detail["error_code"] == "EMAIL_EXISTS"


class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self):
        db = make_mock_db()
        service = UserService(db)

        mock_user = MagicMock(spec=User)
        mock_user.id = "uuid-1"
        mock_user.username = "testuser"
        mock_user.email = "test@test.com"
        mock_user.phone = "3001234567"
        mock_user.status = UserStatus.ACTIVA
        mock_user.password_hash = hash_password("Secure1234")
        mock_user.failed_attempts = 0

        with patch.object(service.repo, "find_by_username", return_value=mock_user), \
             patch.object(service.repo, "save", new_callable=AsyncMock):
            result = await service.login(LoginRequest(username="testuser", password="Secure1234"), TRACE_ID)
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        db = make_mock_db()
        service = UserService(db)

        mock_user = MagicMock(spec=User)
        mock_user.status = UserStatus.ACTIVA
        mock_user.password_hash = hash_password("Secure1234")
        mock_user.failed_attempts = 0

        with patch.object(service.repo, "find_by_username", return_value=mock_user), \
             patch.object(service.repo, "save", new_callable=AsyncMock):
            with pytest.raises(HTTPException) as exc:
                await service.login(LoginRequest(username="testuser", password="wrong"), TRACE_ID)
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_blocked_user(self):
        db = make_mock_db()
        service = UserService(db)

        mock_user = MagicMock(spec=User)
        mock_user.status = UserStatus.BLOQUEADO

        with patch.object(service.repo, "find_by_username", return_value=mock_user):
            with pytest.raises(HTTPException) as exc:
                await service.login(LoginRequest(username="testuser", password="any"), TRACE_ID)
            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        db = make_mock_db()
        service = UserService(db)

        with patch.object(service.repo, "find_by_username", return_value=None):
            with pytest.raises(HTTPException) as exc:
                await service.login(LoginRequest(username="ghost", password="pass"), TRACE_ID)
            assert exc.value.status_code == 401
