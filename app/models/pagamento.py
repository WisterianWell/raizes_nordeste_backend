from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id_pagamento: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido"), index=True)
    id_transacao: Mapped[str] = mapped_column(String, index=True)
    forma_pagamento: Mapped[str] = mapped_column(String)
    valor_original: Mapped[float] = mapped_column(Numeric(10, 2))
    valor: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
