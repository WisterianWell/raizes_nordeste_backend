from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.produto import Produto

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id_item_pedido: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_pedido: Mapped[int] = mapped_column(ForeignKey("pedidos.id_pedido"), index=True)
    id_produto: Mapped[int] = mapped_column(ForeignKey("produtos.id_produto"), index=True)
    quantidade: Mapped[int] = mapped_column(Integer)
    preco_unitario: Mapped[float] = mapped_column(Numeric(10, 2))
    produto: Mapped[Produto] = relationship(lazy="selectin")

    @property
    def nome_produto(self) -> str:
        return self.produto.nome

    @property
    def subtotal(self) -> float:
        return float(self.preco_unitario) * self.quantidade
