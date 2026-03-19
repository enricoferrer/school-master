from fastapi import FastAPI
from app.routers import usuario_router
from app.routers import funcionario_router
from app.routers import professor_router
from app.routers import disciplina_router
from app.routers import professor_disciplina_router
from app.routers import turma_router
from app.routers import turma_professores_router
from app.routers import aluno_router

app = FastAPI(title="School-Master API")

app.include_router(usuario_router.router)
app.include_router(funcionario_router.router)
app.include_router(professor_router.router)
app.include_router(disciplina_router.router)
app.include_router(professor_disciplina_router.router)
app.include_router(turma_router.router)
app.include_router(turma_professores_router.router)
app.include_router(aluno_router.router)