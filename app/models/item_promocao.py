from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import TipoDesconto
from app.models.base import Base
from app.models.produto import Produto

class ItemPromocao(Base):
    __tablename__ = "itens_promocao"
    id_item_promo: Mapped[int] = mapped_column(primary_key=True, index=True)
    id_promocao: Mapped[int] = mapped_column(ForeignKey("promocoes.id_promocao"), index=True)
    id_produto: Mapped[int] = mapped_column(ForeignKey("produtos.id_produto"), index=True)
    tipo_desc: Mapped[str] = mapped_column(String, default=TipoDesconto.PERCENTUAL.value)
    valor_desc: Mapped[float] = mapped_column(Numeric(10, 2))
    produto: Mapped[Produto] = relationship(lazy="selectin")

    @property
    def nome_produto(self) -> str:
        return self.produto.nome
