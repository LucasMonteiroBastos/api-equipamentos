"""Schemas: o formato dos dados que ENTRAM e SAEM da API.

Separamos de models.py de propósito: o cliente não deve conseguir
enviar campos como `id` ou `criado_em`, que o próprio sistema define.
O Pydantic valida tudo automaticamente e devolve erro 422 se vier errado.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["operando", "manutencao", "parado"]


class EquipamentoCriar(BaseModel):
    """Dados exigidos para cadastrar (POST)."""
    tag: str = Field(min_length=2, max_length=30, examples=["BR-2001-01"])
    nome: str = Field(min_length=2, max_length=100, examples=["Britador cônico primário"])
    tipo: str = Field(min_length=2, max_length=50, examples=["britador"])
    status: Status = "operando"


class EquipamentoAtualizar(BaseModel):
    """Dados para atualização parcial (PATCH): todos opcionais."""
    tag: str | None = Field(default=None, min_length=2, max_length=30)
    nome: str | None = Field(default=None, min_length=2, max_length=100)
    tipo: str | None = Field(default=None, min_length=2, max_length=50)
    status: Status | None = None


class EquipamentoSaida(EquipamentoCriar):
    """O que a API devolve: os dados + campos gerados pelo sistema."""
    model_config = ConfigDict(from_attributes=True)  # permite converter o model do SQLAlchemy

    id: int
    criado_em: datetime
