from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "hadis_db"
    mysql_user: str = "hadis_user"
    mysql_password: str = "hadis_pass"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+asyncmy://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_ar: str = "hadisler_ar"
    qdrant_collection_en: str = "hadisler_en"

    # JWT
    secret_key: str = "changeme-please-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # NLP
    embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"
    embedding_dim: int = 768

    # API
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    debug: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


settings = Settings()
