from fastapi import FastAPI
from app.routers import usuario_router
from app.routers import funcionario_router

app = FastAPI(title="School-Master API")

app.include_router(usuario_router.router)
app.include_router(funcionario_router.router)