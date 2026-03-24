#!/usr/bin/env python
import os
import sys
import subprocess
import time

db_host = os.getenv("DB_HOST", "db")
db_user = os.getenv("DB_USER", "user")
db_pass = os.getenv("DB_PASS", "password")
db_name = os.getenv("DB_NAME", "school_master")
db_port = os.getenv("DB_PORT", "5432")

print(f"[*] Aguardando database ({db_host}:{db_port}) estar pronto...")

max_retries = 60
retry = 0

while retry < max_retries:
    result = subprocess.run(
        ["pg_isready", "-h", db_host, "-U", db_user, "-d", db_name, "-p", db_port],
        capture_output=True,
        env={**os.environ, "PGPASSWORD": db_pass},  # 🔥 FIX PRINCIPAL
    )

    if result.returncode == 0:
        print("[✓] Database está pronto!")
        break

    retry += 1
    print(f"[!] Database ainda não está pronto... ({retry}/{max_retries})")
    time.sleep(2)

if retry == max_retries:
    print("[✗] Timeout aguardando database!")
    sys.exit(1)

# migrations
print("[*] Executando migrations com Alembic...")
env = os.environ.copy()
env["PYTHONPATH"] = "/app"

result = subprocess.run(
    ["python", "-m", "alembic", "-c", "/app/alembic/alembic.ini", "upgrade", "head"],
    env=env,
)

if result.returncode != 0:
    print("[✗] Erro ao executar migrations!")
    sys.exit(1)

print("[✓] Migrations executadas com sucesso!")

# start app
print("[*] Iniciando FastAPI com Uvicorn...")
os.execvp(
    "uvicorn",
    ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
)