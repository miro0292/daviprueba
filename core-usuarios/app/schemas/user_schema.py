from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterRequest(BaseModel):
    document_number: str
    email: EmailStr
    phone: str
    username: str
    password: str

    @field_validator("document_number")
    @classmethod
    def document_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El número de documento es obligatorio")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v: str) -> str:
        if not re.match(r"^\d{7,15}$", v):
            raise ValueError("El teléfono debe contener entre 7 y 15 dígitos")
        return v

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class RegisterResponse(BaseModel):
    id: str
    username: str
    email: str
    status: str
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    username: str
    email: str
    phone: str
    status: str
