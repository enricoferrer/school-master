from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database                      import get_db
from app.dependencies.auth                  import require_permission, TokenData
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.frequencia_repository import FrequenciaRepository
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.repositories.turma_repository import TurmaRepository
from app.repositories.notificacao_repository import NotificacaoRepository
from app.services.frequencia_service import FrequenciaService
from app.services.notificacao_service import NotificacaoService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_frequencia_service(db: AsyncSession = Depends(get_db)):
    return FrequenciaService(
        FrequenciaRepository(db), 
        AlunoRepository(db), 
        DisciplinaRepository(db), 
        TurmaProfessoresRepository(db),
        TurmaRepository(db),
        NotificacaoService(NotificacaoRepository(db))
    )


@router.get("/attendance")
async def analytics_frequencia(
    current_user: Annotated[TokenData, Depends(require_permission("analytics:read"))],
    service:      FrequenciaService = Depends(get_frequencia_service),
    data_inicio:  date | None = Query(None),
    data_fim:     date | None = Query(None),
):
    return await service.analytics(data_inicio, data_fim)