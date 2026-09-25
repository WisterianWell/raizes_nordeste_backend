from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class MovPontos(Base):
    __tablename__ = "mov_pontos"
    id_mov_pontos: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_cliente: Mapped[int] = mapped_column(ForeignKey("clientes.id_cliente"), index=True)
    id_pedido: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id_pedido"), index=True)
    tipo: Mapped[str] = mapped_column(String, index=True)
    pontos: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
