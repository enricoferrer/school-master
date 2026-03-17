from uuid import UUID

from pydantic import BaseModel, field_validator
from app.validators.common_validator import not_empty

class TurmaModel(BaseModel):
    sala: str
    serie: str
    
    @field_validator("sala", "serie")
    @classmethod
    def val_not_empty(cls, v): return not_empty(v)
    
class TurmaCreate(TurmaModel):
    pass

class TurmaResponse(TurmaModel):
    id: UUID