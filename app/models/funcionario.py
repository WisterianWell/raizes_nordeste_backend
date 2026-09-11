from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class Funcionario(Base):
    __tablename__ = "funcionarios"
    id_funcionario: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    cpf: Mapped[str] = mapped_column(String, unique=True, index=True)
    telefone: Mapped[str] = mapped_column(String)
    hashed_senha: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    cargo: Mapped[str] = mapped_column(String, index=True)
