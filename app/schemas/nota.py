from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, field_validator
from typing import Literal
from app.validators.nota_validator import validate_valor_nota_valido


SITUACAO = Literal["Aprovado", "Recuperação", "Reprovado"]


class NotaCreate(BaseModel):
    aluno_id:     UUID
    avaliacao_id: UUID
    valor:        Decimal

    @field_validator("valor")
    @classmethod
    def valor_valido(cls, v): return validate_valor_nota_valido(v)


class NotaUpdate(BaseModel):
    valor: Decimal

    @field_validator("valor")
    @classmethod
    def valor_valido(cls, v): return validate_valor_nota_valido(v)


class NotaResponse(BaseModel):
    id:              UUID
    fk_aluno:        UUID
    fk_avaliacao:    UUID
    valor:           Decimal | None
    data_lancamento: datetime

    model_config = {"from_attributes": True}


# ── Boletim ──────────────────────────────────────────────────────────────────

class MediaPorPeriodo(BaseModel):
    periodo:         str
    media_ponderada: float
    situacao:        SITUACAO


class DisciplinaBoletim(BaseModel):
    disciplina_id:   UUID
    disciplina_nome: str
    bimestres:       list[MediaPorPeriodo]
    media_final:     float
    situacao_final:  SITUACAO
    media_turma:     float


class BoletimResponse(BaseModel):
    aluno_id:      UUID
    aluno_nome:    str
    ano_letivo:    int
    disciplinas:   list[DisciplinaBoletim]


# ── Analytics ────────────────────────────────────────────────────────────────

class AlunoAbaixoMedia(BaseModel):
    aluno_id:   UUID
    aluno_nome: str
    media:      float


class AnalyticsDisciplina(BaseModel):
    disciplina_id:    UUID
    disciplina_nome:  str
    periodo:          str
    media:            float
    mediana:          float
    desvio_padrao:    float
    percentil_25:     float
    percentil_75:     float
    alunos_abaixo:    list[AlunoAbaixoMedia]


class AnalyticsNotasResponse(BaseModel):
    disciplinas: list[AnalyticsDisciplina]