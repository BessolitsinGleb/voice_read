from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings_(BaseSettings):

    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGO: str = "HS256" 
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str 
    SMTP_PASSWORD: str 

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

Settings = Settings_()
