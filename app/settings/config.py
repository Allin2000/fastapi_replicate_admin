from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "FastAdmin"
    PROJECT_NAME: str = "FastAdmin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    ADD_LOG_ORIGINS_INCLUDE: list = ["*"]  # APILoggerMiddleware and APILoggerAddResponseMiddleware
    ADD_LOG_ORIGINS_DECLUDE: list = ["/system-manage", "/redoc", "/doc", "/openapi.json"]

    # DEBUG: bool = True

    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    BASE_DIR: Path = PROJECT_ROOT.parent
    LOGS_ROOT: Path = BASE_DIR / "app/logs"
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")



    @property
    def TORTOISE_ORM(self) -> dict:
        return {
            "connections": {
                "conn_system": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_NAME
                    }
                }
            },
            "apps": {
                "app_system": {
                    "models": ["app.sqlmodel.admin", "aerich.models"],
                    "default_connection": "conn_system"
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai"
        }





APP_SETTINGS = Settings()
TORTOISE_ORM = APP_SETTINGS.TORTOISE_ORM
