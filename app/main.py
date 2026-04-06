from fastapi import FastAPI
import logging
from fastapi.concurrency import asynccontextmanager
from app.core.database import AsyncSessionLocal
from app.core.redis_client import close_redis
from app.middleware.audit_middleware import AuditMiddleware
from app.routers import analytics_router, frequencia_router, nota_router, notificacao_router, portal_router, reports_router, usuario_router
from app.routers import funcionario_router
from app.routers import professor_router
from app.routers import disciplina_router
from app.routers import professor_disciplina_router
from app.routers import turma_router
from app.routers import turma_professores_router
from app.routers import aluno_router
from app.routers import auth_router
from app.routers import admin_roles_router
from app.routers import audit_log_router
from app.routers import aluno_responsavel_router
from app.services.rbac_service import seed_role_permissions

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with AsyncSessionLocal() as db:
            await seed_role_permissions(db)
            logging.info("Seed de permissões OK")
    except Exception as e:
        logging.error("FALHA no seed de permissões: %s", e, exc_info=True)
        raise
    yield
    await close_redis()

app = FastAPI(title="School-Master API", lifespan=lifespan)

app.add_middleware(AuditMiddleware)

app.include_router(usuario_router.router)
app.include_router(funcionario_router.router)
app.include_router(professor_router.router)
app.include_router(disciplina_router.router)
app.include_router(professor_disciplina_router.router)
app.include_router(turma_router.router)
app.include_router(turma_professores_router.router)
app.include_router(aluno_router.router)
app.include_router(aluno_responsavel_router.router)
app.include_router(auth_router.router)
app.include_router(admin_roles_router.router)
app.include_router(audit_log_router.router)
app.include_router(frequencia_router.router)
app.include_router(analytics_router.router)
app.include_router(reports_router.router)
app.include_router(nota_router.router)
app.include_router(notificacao_router.router)
app.include_router(portal_router.router)