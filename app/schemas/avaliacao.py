from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, field_validator
from typing import Literal
from app.validators.avaliacao_validator import validate_peso_positivo


PERIODOS = Literal["1B", "2B", "3B", "4B"]
TIPOS    = Literal["prova", "trabalho", "participacao"]


class AvaliacaoCreate(BaseModel):
    turma_professor_id: UUID
    titulo:             str
    tipo:               TIPOS
    peso:               Decimal
    periodo:            PERIODOS
    data_aplicacao:     date | None = None

    @field_validator("peso")
    @classmethod
    def peso_positivo(cls, v): return validate_peso_positivo(v)


class AvaliacaoResponse(BaseModel):
    id:                 UUID
    fk_turma_professor: UUID
    titulo:             str
    tipo:               str | None
    peso:               Decimal
    periodo:            str
    data_aplicacao:     date | None

    model_config = {"from_attributes": True}