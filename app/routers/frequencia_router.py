# routers/attendance_router.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database               import get_db
from app.dependencies.auth           import require_permission, TokenData
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.frequencia_repository import FrequenciaRepository
from app.repositories.notificacao_repository import NotificacaoRepository
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.repositories.turma_repository import TurmaRepository
from app.schemas.frequencia          import FrequenciaCreate, FrequenciaResponse
from app.services.frequencia_service import FrequenciaService
from app.services.notificacao_service import NotificacaoService

router = APIRouter(prefix="/attendance", tags=["Frequência"])


def get_frequencia_service(db: AsyncSession = Depends(get_db)):
    return FrequenciaService(
        FrequenciaRepository(db), 
        AlunoRepository(db), 
        DisciplinaRepository(db), 
        TurmaProfessoresRepository(db),
        TurmaRepository(db),
        NotificacaoService(NotificacaoRepository(db))
    )


@router.post("", response_model=FrequenciaResponse, status_code=201)
async def registrar_frequencia(
    body:         FrequenciaCreate,
    current_user: Annotated[TokenData, Depends(require_permission("frequencia:write"))],
    service:      FrequenciaService = Depends(get_frequencia_service),
):
    return await service.registrar(body, registrado_por=current_user.user_id)