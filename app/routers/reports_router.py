from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
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
from app.utils.pdf_generator                import gerar_pdf_frequencia

router = APIRouter(prefix="/reports", tags=["Relatórios"])


def get_frequencia_service(db: AsyncSession = Depends(get_db)) -> FrequenciaService:
    return FrequenciaService(
        FrequenciaRepository(db), 
        AlunoRepository(db), 
        DisciplinaRepository(db), 
        TurmaProfessoresRepository(db),
        TurmaRepository(db),
        NotificacaoService(NotificacaoRepository(db))
    )


@router.get("/attendance", response_class=Response)
async def relatorio_frequencia_pdf(
    current_user: Annotated[TokenData, Depends(require_permission("report:read"))],
    service:      FrequenciaService = Depends(get_frequencia_service),
    data_inicio:  date = Query(...),
    data_fim:     date = Query(...),
):
    dados = await service.dados_relatorio(data_inicio, data_fim)
    pdf   = gerar_pdf_frequencia(dados)

    return Response(
        content     = pdf,
        media_type  = "application/pdf",
        headers     = {
            "Content-Disposition": f"attachment; filename=frequencia_{data_inicio}_{data_fim}.pdf"
        },
    )