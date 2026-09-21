from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str | None = None
    role: str | None = None

class RefreshRequest(BaseModel):
    refresh_token: str
