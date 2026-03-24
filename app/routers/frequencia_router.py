# routers/attendance_router.py
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database               import get_db
from app.dependencies.auth           import require_permission, TokenData
from app.repositories.frequencia_repository import FrequenciaRepository
from app.schemas.frequencia          import FrequenciaCreate, FrequenciaResponse
from app.services.frequencia_service import FrequenciaService

router = APIRouter(prefix="/attendance", tags=["Frequência"])


def get_frequencia_service(db: AsyncSession = Depends(get_db)) -> FrequenciaService:
    return FrequenciaService(FrequenciaRepository(db))


@router.post("", response_model=FrequenciaResponse, status_code=201)
async def registrar_frequencia(
    body:         FrequenciaCreate,
    current_user: Annotated[TokenData, Depends(require_permission("frequencia:write"))],
    service:      FrequenciaService = Depends(get_frequencia_service),
):
    return await service.registrar(body, registrado_por=current_user.user_id)