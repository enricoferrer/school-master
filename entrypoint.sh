#!/bin/bash
set -e

echo "Aguardando database estar pronto..."
until pg_isready -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME"; do
  echo "Database ainda não está pronta, aguardando..."
  sleep 2
done

echo "Database está pronto! Executando migrations..."
alembic upgrade head

echo "Migrations concluídas! Iniciando aplicação..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
