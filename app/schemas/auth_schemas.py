from pydantic import BaseModel

class TokenUsuario(BaseModel):
    id: int
    nome: str
    perfil: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: TokenUsuario

class TokenData(BaseModel):
    sub: str | None = None
    role: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str
