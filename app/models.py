"""Models: como os dados ficam guardados no banco (as tabelas)."""
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Equipamento(Base):
    __tablename__ = "equipamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str] = mapped_column(String(30), unique=True, index=True)  # ex.: BR-2001-01
    nome: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[str] = mapped_column(String(50))  # ex.: britador, correia, bomba
    status: Mapped[str] = mapped_column(String(20), default="operando")
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
