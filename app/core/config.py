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
    jwt_refresh_expiration_days: int = 7

    # Admin padráo
    admin_email: str | None = None
    admin_senha: str | None = None
    admin_nome: str = "Administrador"
    admin_cpf: str = "00000000000"
    admin_telefone: str = "00000000000"

@lru_cache
def get_settings() -> Settings:
    return Settings()