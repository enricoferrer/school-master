#!/usr/bin/env python
import os
import sys
import subprocess
import time

# Get database credentials from environment
db_host = os.getenv('DB_HOST', 'localhost')
db_user = os.getenv('DB_USER', 'user')
db_name = os.getenv('DB_NAME', 'school_master')
db_port = os.getenv('DB_PORT', '5432')

print(f"[*] Aguardando database ({db_host}:{db_port}) estar pronto...")

# Wait for database to be ready
max_retries = 30
retry = 0
while retry < max_retries:
    result = subprocess.run(
        ['pg_isready', '-h', db_host, '-U', db_user, '-d', db_name, '-p', db_port],
        capture_output=True
    )
    if result.returncode == 0:
        print("[✓] Database está pronto!")
        break
    retry += 1
    if retry < max_retries:
        print(f"[!] Database ainda não está pronto... ({retry}/{max_retries})")
        time.sleep(1)
    else:
        print("[✗] Timeout aguardando database!")
        sys.exit(1)

# Run migrations
print("[*] Executando migrations com Alembic...")
env = os.environ.copy()
env['PYTHONPATH'] = '/app'
result = subprocess.run(
    ['python', '-m', 'alembic', '-c', '/app/alembic/alembic.ini', 'upgrade', 'head'],
    env=env
)
if result.returncode != 0:
    print("[✗] Erro ao executar migrations!")
    sys.exit(1)
print("[✓] Migrations executadas com sucesso!")

# Start the application
print("[*] Iniciando FastAPI com Uvicorn...")
os.execvp('uvicorn', ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'])
