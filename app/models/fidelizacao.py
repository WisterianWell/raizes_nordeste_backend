from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class Fidelizacao(Base):
    __tablename__ = "pontos_fidelizacao"
    id_cliente: Mapped[int] = mapped_column(ForeignKey("clientes.id_cliente"), primary_key=True)
    pontos: Mapped[int] = mapped_column(Integer, default=0)
