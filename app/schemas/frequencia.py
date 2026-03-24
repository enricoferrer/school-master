from datetime import date
from uuid import UUID
from pydantic import BaseModel, field_validator
from app.validators.common_validator import data_nao_futura


class FrequenciaCreate(BaseModel):
    aluno_id:           UUID
    turma_professor_id: UUID
    data:               date
    presenca:           bool = True

    @field_validator("data")
    @classmethod
    def val_data(cls, v): return data_nao_futura(v)        

class FrequenciaResponse(BaseModel):
    id:                 UUID
    fk_aluno:           UUID
    fk_turma_professor: UUID
    data:               date
    presenca:           bool
    metodo_registro:    str

    model_config = {"from_attributes": True}