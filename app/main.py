from fastapi import FastAPI
from app.routers import usuario_router
from app.routers import funcionario_router
from app.routers import professor_router
from app.routers import disciplina_router

app = FastAPI(title="School-Master API")

app.include_router(usuario_router.router)
app.include_router(funcionario_router.router)
app.include_router(professor_router.router)
app.include_router(disciplina_router.router)