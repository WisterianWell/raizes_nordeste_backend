from sqlalchemy import Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.produto import Produto

class ItemCardapio(Base):
    __tablename__ = "itens_cardapio"
    id_produto: Mapped[int] = mapped_column(ForeignKey("produtos.id_produto"), primary_key=True)
    id_unidade: Mapped[int] = mapped_column(ForeignKey("unidades.id_unidade"), primary_key=True)
    preco: Mapped[float] = mapped_column(Numeric(10, 2))
    disponivel: Mapped[bool] = mapped_column(Boolean, default=True)
    produto: Mapped[Produto] = relationship(lazy="selectin")

    @property
    def nome(self) -> str:
        return self.produto.nome

    @property
    def categoria(self) -> str:
        return self.produto.categoria
