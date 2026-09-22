from datetime import datetime

from pydantic import BaseModel

class LogAuditoriaResponse(BaseModel):
    id_log: int
    tipo_usuario: str | None
    id_usuario: int | None
    acao: str
    entidade: str
    id_entidade: int | None
    id_unidade: int | None
    detalhes: dict | None
    criado_em: datetime
    model_config = {"from_attributes": True}
