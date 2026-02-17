from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Neighborhood Library API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg2://library:library@localhost:5432/library"
    default_loan_days: int = 14

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
