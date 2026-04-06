from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class NotaPortal(BaseModel):
    disciplina:      str
    avaliacao:       str
    tipo:            str | None
    valor:           Decimal | None
    periodo:         str
    data_lancamento: datetime


class FrequenciaPortal(BaseModel):
    disciplina:  str
    total_aulas: int
    presencas:   int
    percentual:  float


class PortalAlunoResponse(BaseModel):
    aluno_id:         UUID
    aluno_nome:       str
    tipo_responsavel: str
    notas:            list[NotaPortal]
    frequencias:      list[FrequenciaPortal]