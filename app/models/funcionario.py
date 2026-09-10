from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String

from app.models.base import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"
    id_funcionario = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)
    telefone = Column(String)
    hashed_senha = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    cargo = Column(String, index=True)