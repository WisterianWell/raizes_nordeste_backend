from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

#Configurações da aplicação via pydantic-settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Aplicação
    app_name: str = "SistemaRaizesNorte"
    app_version: str = "1.0.0"
    debug: bool = False
    enviroment: str = "production"

    # Database
    database_url: str

    # Autenticação
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

@lru_cache
def get_settings() -> Settings:
    return Settings()