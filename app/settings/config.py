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
    PUBLIC_SCHEMA: str = "public"
    ADMIN_SCHEMA: str = "admin" 

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
                        "database": self.DB_NAME,
                        "server_settings": {"search_path": f"{self.ADMIN_SCHEMA}"}
                    }
                }
            },
            "conn_public": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": self.DB_HOST,
                        "port": self.DB_PORT,
                        "user": self.DB_USER,
                        "password": self.DB_PASSWORD,
                        "database": self.DB_NAME,
                        # 对于 public 模式，默认搜索路径设为 public，同时包含 admin 以便跨 schema 引用
                        "server_settings":{"search_path": f"{self.PUBLIC_SCHEMA}"}
                    },
                    "maxsize": 10 # 可以调整连接池大小
                },
            "apps": {
                "app_system": {
                    "models": ["app.sqlmodel.admin", "aerich.models"],
                    "default_connection": "conn_system"
                },
                # 新增 public 应用
            #     "app_public": {
            #         "models": ["app.models.public"],  # 指向新模型
            #         "default_connection": "conn_public"  # 使用第二个连接
            # }

            },
            "use_tz": False,
            "timezone": "Asia/Shanghai"
        }





APP_SETTINGS = Settings()
TORTOISE_ORM = APP_SETTINGS.TORTOISE_ORM
