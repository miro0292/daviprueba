from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    max_failed_attempts: int = 5
    service_name: str = "core-usuarios"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
