from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import StatusPedido
from app.models.base import Base
from app.models.item_pedido import ItemPedido
from app.models.pagamento import Pagamento

class Pedido(Base):
    __tablename__ = "pedidos"
    id_pedido: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_cliente: Mapped[int | None] = mapped_column(ForeignKey("clientes.id_cliente"), index=True)
    id_unidade: Mapped[int] = mapped_column(ForeignKey("unidades.id_unidade"), index=True)
    canal: Mapped[str] = mapped_column(String, index=True)
    status_pedido: Mapped[str] = mapped_column(String, default=StatusPedido.PENDENTE.value, index=True)
    status_pagamento: Mapped[str | None] = mapped_column(String, index=True)
    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    itens: Mapped[list[ItemPedido]] = relationship(lazy="selectin", cascade="all, delete-orphan")
    pagamentos: Mapped[list[Pagamento]] = relationship(lazy="selectin", cascade="all, delete-orphan")
