"""
Converte tipos Python não-serializáveis em primitivos JSON-safe.
Deve ser aplicado em qualquer dict antes de persistir em colunas JSONB.
"""
from uuid import UUID
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any


def to_jsonb_safe(data: Any) -> Any:
    """
    Recursivamente converte tipos não-serializáveis em primitivos JSON.

    UUID      → str
    datetime  → str ISO 8601 (com timezone UTC)
    date      → str ISO 8601
    Decimal   → float
    bytes     → str hex
    set/tuple → list
    outros    → str (fallback)
    """
    if data is None:
        return None

    if isinstance(data, dict):
        return {k: to_jsonb_safe(v) for k, v in data.items()}

    if isinstance(data, (list, tuple, set)):
        return [to_jsonb_safe(i) for i in data]

    if isinstance(data, UUID):
        return str(data)

    if isinstance(data, datetime):
        # Garante UTC no timezone-aware, converte naive para UTC assumido
        if data.tzinfo is None:
            data = data.replace(tzinfo=timezone.utc)
        return data.isoformat()

    if isinstance(data, date):
        return data.isoformat()

    if isinstance(data, Decimal):
        return float(data)

    if isinstance(data, bytes):
        return data.hex()

    # Primitivos nativos JSON (str, int, float, bool) passam direto
    if isinstance(data, (str, int, float, bool)):
        return data

    # Fallback seguro para qualquer outro tipo
    return str(data)