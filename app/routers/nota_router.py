from typing import Annotated
from uuid import UUID

from alembic.util import status
from fastapi import APIRouter, Depends, HTTPException, Query
from passlib import exc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database                 import get_db
from app.dependencies.auth             import require_permission, TokenData
from app.models.notificacao import Notificacao
from app.repositories.aluno_repository import AlunoRepository
from app.repositories.disciplina_repository import DisciplinaRepository
from app.repositories.nota_repository import NotaRepository
from app.repositories.notificacao_repository import NotificacaoRepository
from app.repositories.turma_professores_repository import TurmaProfessoresRepository
from app.schemas.nota                  import (
    NotaCreate, NotaUpdate, NotaResponse,
)
from app.schemas.avaliacao import AvaliacaoCreate, AvaliacaoResponse
from app.services.nota_service         import NotaService
from app.exceptions.NotOwnerException import NotOwnerException
from app.exceptions.NotFoundException import NotFoundException
from app.exceptions.DuplicateFieldException import DuplicateFieldException
from app.services.notificacao_service import NotificacaoService

router = APIRouter(tags=["Notas & Avaliações"])


def get_nota_service(db: AsyncSession = Depends(get_db)) -> NotaService:
    return NotaService(NotaRepository(db), AlunoRepository(db), NotificacaoService(NotificacaoRepository(db)), DisciplinaRepository(db), TurmaProfessoresRepository(db))


# ── Avaliações ────────────────────────────────────────────────────────────────

@router.post("/avaliacoes", response_model=AvaliacaoResponse, status_code=201)
async def criar_avaliacao(
    body:         AvaliacaoCreate,
    current_user: Annotated[TokenData, Depends(require_permission("grade:write"))],
    service:      NotaService = Depends(get_nota_service),
):
    try:
        return await service.criar_avaliacao(body, current_user.user_id)
    except NotOwnerException as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


# ── Notas ─────────────────────────────────────────────────────────────────────

@router.post("/notas", response_model=NotaResponse, status_code=201)
async def lancar_nota(
    body:         NotaCreate,
    current_user: Annotated[TokenData, Depends(require_permission("grade:write"))],
    service:      NotaService = Depends(get_nota_service),
):
    try:
        return await service.lancar_nota(body, current_user.user_id)
    except NotOwnerException as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except DuplicateFieldException as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.put("/notas/{nota_id}", response_model=NotaResponse)
async def editar_nota(
    nota_id:      UUID,
    body:         NotaUpdate,
    current_user: Annotated[TokenData, Depends(require_permission("grade:write"))],
    service:      NotaService = Depends(get_nota_service),
):
    try:
        return await service.editar_nota(nota_id, body, current_user.user_id)
    except NotOwnerException as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except DuplicateFieldException as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


# ── Boletim ───────────────────────────────────────────────────────────────────

@router.get("/alunos/{aluno_id}/boletim", response_model=None)
async def boletim_aluno(
    aluno_id:     UUID,
    current_user: Annotated[TokenData, Depends(require_permission("grade:read"))],
    service:      NotaService = Depends(get_nota_service),
    db:           AsyncSession = Depends(get_db),
    ano_letivo:   int = Query(..., description="Ex: 2025"),
):
    try:
        aluno_nome = await service._buscar_aluno_nome_ou_404(aluno_id)
        return await service.boletim(aluno_id, ano_letivo, aluno_nome)
    except NotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


# ── Analytics ─────────────────────────────────────────────────────────────────

@router.get("/analytics/notas")
async def analytics_notas(
    current_user: Annotated[TokenData, Depends(require_permission("analytics:read"))],
    service:      NotaService = Depends(get_nota_service),
    periodo:      str | None  = Query(None, pattern="^[1-4]B$"),
):
    return await service.analytics(periodo)