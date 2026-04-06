from datetime import datetime, time
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, EmailStr

CANAIS        = Literal["EMAIL"]
TIPOS_EVENTO  = Literal["NOTA_LANCADA", "FALTA", "FREQUENCIA_CRITICA", "FATURA", "COMUNICADO", "NOTA_EDITADA"]
STATUS        = Literal["PENDENTE", "ENVIADO", "ENTREGUE", "FALHOU"]


class NotificacaoResponse(BaseModel):
    id:                 UUID
    fk_usuario_destino: UUID
    tipo:               str | None
    canal:              str | None
    titulo:             str | None
    mensagem:           str | None
    status:             str
    tentativas:         int
    enviado_em:         datetime | None
    erro_detalhe:       str | None
    criado_em:          datetime

    model_config = {"from_attributes": True}


class PreferenciaCreate(BaseModel):
    canal:          CANAIS        = "EMAIL"
    tipo_evento:    TIPOS_EVENTO
    ativo:          bool          = True
    horario_inicio: time | None   = None
    horario_fim:    time | None   = None


class PreferenciaResponse(BaseModel):
    id:             UUID
    canal:          str
    tipo_evento:    str
    ativo:          bool
    horario_inicio: time | None
    horario_fim:    time | None

    model_config = {"from_attributes": True}