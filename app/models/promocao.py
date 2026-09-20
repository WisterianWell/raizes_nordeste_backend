from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.item_promocao import ItemPromocao

class Promocao(Base):
    __tablename__ = "promocoes"
    id_promocao: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_unidade: Mapped[int | None] = mapped_column(ForeignKey("unidades.id_unidade"), index=True)
    data_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    data_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    itens: Mapped[list[ItemPromocao]] = relationship(lazy="selectin", cascade="all, delete-orphan")
