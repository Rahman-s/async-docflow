from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    UPLOAD_DIR: str = "uploads"
    EXPORT_DIR: str = "exports"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()