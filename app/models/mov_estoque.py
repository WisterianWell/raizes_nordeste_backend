from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class MovEstoque(Base):
    __tablename__ = "mov_estoque"
    id_mov_estoque: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_produto: Mapped[int] = mapped_column(ForeignKey("produtos.id_produto"), index=True)
    id_unidade: Mapped[int] = mapped_column(ForeignKey("unidades.id_unidade"), index=True)
    id_pedido: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id_pedido"), index=True)
    tipo: Mapped[str] = mapped_column(String, index=True)
    quantidade: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
