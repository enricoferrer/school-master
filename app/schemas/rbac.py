from uuid import UUID
from pydantic import BaseModel, field_validator
from app.validators.rbac_validator import validate_roles


class RoleAssignRequest(BaseModel):
    usuario_id: UUID
    role_nome: str

    @field_validator("role_nome")
    @classmethod
    def validar_role(cls, v: str): return validate_roles(v)

class RoleAssignResponse(BaseModel):
    message: str
    usuario_id: UUID
    role_anterior: str | None
    role_novo: str


class RoleRevokeResponse(BaseModel):
    message: str
    usuario_id: UUID
    role_anterior: str | None
    role_atual: str = "ALUNO"