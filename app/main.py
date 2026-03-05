from fastapi import FastAPI
from app.routers import usuario_router

app = FastAPI(title="School-Master API")

app.include_router(usuario_router.router)