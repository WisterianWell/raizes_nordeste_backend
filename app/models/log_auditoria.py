from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class LogAuditoria(Base):
    __tablename__ = "logs_auditoria"
    id_log: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo_usuario: Mapped[str | None] = mapped_column(String, index=True)
    id_usuario: Mapped[int | None] = mapped_column(Integer, index=True)
    acao: Mapped[str] = mapped_column(String, index=True)
    entidade: Mapped[str] = mapped_column(String, index=True)
    id_entidade: Mapped[int | None] = mapped_column(Integer, index=True)
    id_unidade: Mapped[int | None] = mapped_column(Integer, index=True)
    detalhes: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
