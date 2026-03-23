import json
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.database import AsyncSessionLocal
from app.utils.json_sanitizer import to_jsonb_safe
from app.models.audit_log import AuditLog
from app.utils.diff_builder import build_diff
from app.utils.entity_resolver import resolve_entity, fetch_before_state
from app.core.security import decode_token

logger = logging.getLogger("audit")

AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

METHOD_TO_OPERACAO = {
    "POST":   "CREATE",
    "PUT":    "UPDATE",
    "PATCH":  "UPDATE",
    "DELETE": "DELETE",
}


def _extract_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _read_body(request: Request) -> tuple[bytes, Request]:
    """Lê o body sem consumi-lo — devolve um novo Request que pode ser lido novamente."""
    raw = await request.body()

    async def _receive():
        return {"type": "http.request", "body": raw, "more_body": False}

    new_request = Request(request.scope, _receive)
    return raw, new_request


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in AUDITED_METHODS:
            return await call_next(request)

        raw_body, request = await _read_body(request)

        request_body: dict | None = None
        if raw_body:
            try:
                request_body = json.loads(raw_body)
            except Exception:
                request_body = None

        user_id: str | None = None
        role:    str | None = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = decode_token(auth_header.split(" ")[1])
                user_id = payload.get("sub")
                role    = payload.get("role")
            except Exception:
                pass

        path  = request.url.path
        model, tabela, registro_id = resolve_entity(path)

        estado_antes: dict | None = None
        if model and registro_id and request.method in {"PUT", "PATCH", "DELETE"}:
            async with AsyncSessionLocal() as db:
                estado_antes = await fetch_before_state(db, model, registro_id)

        if tabela is None:
            parts = [p for p in path.strip("/").split("/") if p]
            tabela = parts[0] if parts else "unknown"

        start = time.monotonic()
        response: Response = await call_next(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        estado_depois: dict | None = request_body

        if request.method == "DELETE":
            estado_depois = None

        diff = build_diff(estado_antes, estado_depois)

        log_entry = AuditLog(
            id               = uuid.uuid4(),
            fk_usuario       = uuid.UUID(user_id) if user_id else None,
            role_usuario     = role,
            operacao         = METHOD_TO_OPERACAO[request.method],
            tabela_afetada   = tabela,
            registro_id      = uuid.UUID(registro_id) if registro_id else None,
            dados_anteriores  = to_jsonb_safe(estado_antes),   # ← era estado_antes direto
            dados_posteriores = to_jsonb_safe(diff), 
            ip_origem        = _extract_ip(request),
            user_agent       = request.headers.get("User-Agent"),
            metodo_http      = request.method,
            status_http      = response.status_code,
            endpoint         = path,
        )

        import asyncio
        asyncio.ensure_future(_persist_log(log_entry, user_id, request.method))

        logger.info(
            "audit",
            extra={
                "user_id":  user_id,
                "role":     role,
                "method":   request.method,
                "endpoint": path,
                "status":   response.status_code,
                "duration_ms": duration_ms,
                "tabela":   tabela,
                "operacao": METHOD_TO_OPERACAO[request.method],
            },
        )

        return response


async def _persist_log(entry: AuditLog, user_id: str | None, method: str) -> None:
    """Persiste o log e verifica alerta de DELETEs em excesso."""
    try:
        async with AsyncSessionLocal() as db:
            db.add(entry)
            await db.commit()

        if method == "DELETE" and user_id:
            await _check_delete_alert(user_id)

    except Exception as exc:
        logger.error("Falha ao persistir audit_log: %s", exc, exc_info=True)


async def _check_delete_alert(user_id: str) -> None:
    """
    Alerta quando o mesmo user faz >50 DELETEs em menos de 1 hora.
    Usa o próprio banco como fonte de verdade (sem Redis).
    """
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import func, select
    from app.models.audit_log import AuditLog

    uma_hora_atras = datetime.now(timezone.utc) - timedelta(hours=1)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.fk_usuario == uuid.UUID(user_id),
                AuditLog.operacao   == "DELETE",
                AuditLog.timestamp  >= uma_hora_atras,
            )
        )
        count = result.scalar_one()

    if count > 50:
        logger.warning(
            "🚨 ALERTA DE AUDITORIA — Múltiplos DELETEs detectados",
            extra={
                "alert_type": "excessive_deletes",
                "user_id":    user_id,
                "count":      count,
                "window":     "1h",
                "threshold":  50,
            },
        )
      