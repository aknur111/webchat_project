from typing import List, Any
from pydantic import Field, AnyUrl
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_core(v: Any) -> List[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    DOMAIN: str = "localhost"
    ENVIRONMENT: str = "local"
    JWT_SECRET_KEY: str

    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_SERVER: str
    POSTGRESQL_PORT: int
    POSTGRESQL_DATABASE: str

    BACKEND_CORS_ORIGINS: List[AnyUrl] = Field(default_factory=list)

    @property
    def server_host(self) -> str:
        return f"http://{self.DOMAIN}" if self.ENVIRONMENT == "local" else f"https://{self.DOMAIN}"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> AnyUrl:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_SERVER,
            port=self.POSTGRESQL_PORT,
            path=self.POSTGRESQL_DATABASE,
        )

settings = Settings()
