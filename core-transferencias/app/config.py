from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    service_name: str = "core-transferencias"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
