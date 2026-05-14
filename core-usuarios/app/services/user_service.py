from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User, UserStatus
from app.models.account import Account
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.utils.password import hash_password, verify_password
from app.utils.logger import logger
from app.config import settings


class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.db = db

    async def register(self, data: RegisterRequest, trace_id: str) -> RegisterResponse:
        await self._validate_unique_fields(data, trace_id)

        user = User(
            document_number=data.document_number,
            email=data.email,
            phone=data.phone,
            username=data.username,
            password_hash=hash_password(data.password),
            status=UserStatus.ACTIVA,
        )
        user = await self.repo.create(user)

        account = Account(user_id=user.id)
        await self.repo.create_account(account)

        await self.db.commit()

        logger.info("REGISTER", "Usuario registrado exitosamente",
                    trace_id=trace_id, status="SUCCESS", http_status=201)

        return RegisterResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            status=user.status.value,
            message="Usuario registrado exitosamente",
        )

    async def login(self, data: LoginRequest, trace_id: str) -> LoginResponse:
        user = await self.repo.find_by_username(data.username)

        if not user:
            logger.warning("LOGIN", "Usuario no encontrado",
                           trace_id=trace_id, status="FAILED", http_status=401,
                           error_code="USER_NOT_FOUND")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail={"error_code": "INVALID_CREDENTIALS",
                                        "message": "Credenciales inválidas"})

        if user.status == UserStatus.BLOQUEADO:
            logger.warning("LOGIN", "Usuario bloqueado",
                           trace_id=trace_id, status="FAILED", http_status=403,
                           error_code="USER_BLOCKED")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail={"error_code": "USER_BLOCKED",
                                        "message": "Usuario bloqueado temporalmente"})

        if not verify_password(data.password, user.password_hash):
            user.failed_attempts += 1
            if user.failed_attempts >= settings.max_failed_attempts:
                user.status = UserStatus.BLOQUEADO
                logger.warning("LOGIN", "Usuario bloqueado por intentos fallidos",
                               trace_id=trace_id, status="BLOCKED", http_status=403,
                               error_code="MAX_ATTEMPTS_REACHED")
            await self.repo.save(user)
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail={"error_code": "INVALID_CREDENTIALS",
                                        "message": "Credenciales inválidas"})

        user.failed_attempts = 0
        await self.repo.save(user)
        await self.db.commit()

        logger.info("LOGIN", "Login exitoso",
                    trace_id=trace_id, status="SUCCESS", http_status=200)

        return LoginResponse(
            user_id=str(user.id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            status=user.status.value,
        )

    async def _validate_unique_fields(self, data: RegisterRequest, trace_id: str):
        checks = [
            (self.repo.find_by_document(data.document_number), "DOCUMENT_EXISTS",
             "El número de documento ya está registrado"),
            (self.repo.find_by_email(data.email), "EMAIL_EXISTS",
             "El correo electrónico ya está registrado"),
            (self.repo.find_by_phone(data.phone), "PHONE_EXISTS",
             "El número celular ya está registrado"),
            (self.repo.find_by_username(data.username), "USERNAME_EXISTS",
             "El nombre de usuario ya está registrado"),
        ]
        for query, error_code, message in checks:
            if await query:
                logger.warning("REGISTER", message, trace_id=trace_id,
                               status="FAILED", http_status=409, error_code=error_code)
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail={"error_code": error_code, "message": message})
