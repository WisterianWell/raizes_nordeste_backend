from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from app.models.base import Base

class Cliente(Base):
    __tablename__ = "clientes"
    id_cliente = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)
    telefone = Column(String)
    senha_hash = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
