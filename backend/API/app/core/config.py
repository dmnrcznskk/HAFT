from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    IS_PRODUCTION: bool = True
    SUPABASE_URL: str
    SUPABASE_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
