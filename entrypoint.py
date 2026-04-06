# entrypoint.py
import os
import socket
import subprocess
import sys
import time

PROJECT_DIR = os.getenv("PROJECT_DIR", "/app")
MIGRATION_DIR = os.getenv("MIGRATION_DIR", "/app/alembic")

def wait_for_db(host: str, port: int, timeout: int = 60) -> None:
    print(f"[*] Aguardando database ({host}:{port}) estar pronto...")
    start = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("[✓] Database está pronto!")
                return
        except OSError:
            if time.time() - start > timeout:
                print(f"[✗] Timeout aguardando {host}:{port}")
                sys.exit(1)
            time.sleep(2)


def run_migrations() -> None:
    print(f"[*] Executando migrations com Alembic (cwd={PROJECT_DIR})...")

    ini_path = os.path.join(PROJECT_DIR, "alembic.ini")

    if not os.path.exists(ini_path):
        print(f"[✗] alembic.ini não encontrado em {ini_path}")
        sys.exit(1)

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=PROJECT_DIR,
    )

    if result.returncode != 0:
        print("[✗] Erro ao executar migrations!")
        sys.exit(1)

    print("[✓] Migrations executadas com sucesso!")


def start_app() -> None:
    print("[*] Iniciando aplicação...")
    os.chdir(PROJECT_DIR)
    os.execvp(
        "uvicorn",
        [
            "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "1",
        ],
    )


if __name__ == "__main__":
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))

    wait_for_db(db_host, db_port)
    run_migrations()
    start_app()