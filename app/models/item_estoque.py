from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class ItemEstoque(Base):
    __tablename__ = "itens_estoque"
    id_produto: Mapped[int] = mapped_column(ForeignKey("produtos.id_produto"), primary_key=True)
    id_unidade: Mapped[int] = mapped_column(ForeignKey("unidades.id_unidade"), primary_key=True)
    quantidade: Mapped[int] = mapped_column(Integer, default=0)
