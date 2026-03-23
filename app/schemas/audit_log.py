from datetime import datetime
from uuid import UUID
from typing import Any
from app.validators.audit_log_validator import (
    parse_json_field,
    cap_page_size
)

from pydantic import BaseModel, field_validator


class AuditLogResponse(BaseModel):
    id:               UUID
    fk_usuario:       UUID | None
    role_usuario:     str  | None
    operacao:         str
    tabela_afetada:   str
    registro_id:      UUID | None
    dados_anteriores: dict | None
    dados_posteriores:dict | None
    ip_origem:        str  | None
    user_agent:       str  | None
    metodo_http:      str  | None
    status_http:      int  | None
    endpoint:         str  | None
    timestamp:        datetime

    model_config = {"from_attributes": True}

    @field_validator("dados_anteriores", "dados_posteriores", mode="before")
    @classmethod
    def parse_json(cls, v): return parse_json_field(v)


class AuditLogFilters(BaseModel):
    """Query params para GET /audit-logs"""
    user_id:   UUID | None = None
    data_de:   datetime | None = None
    data_ate:  datetime | None = None
    entidade:  str | None = None
    operacao:  str | None = None
    page:      int = 1
    page_size: int = 50

    @field_validator("page_size")
    @classmethod
    def val_page_size(cls, v): return cap_page_size(v)