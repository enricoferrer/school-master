"""
Mascara campos sensíveis em dicionários antes de persistir no audit_log.

Regra de mascaramento:
  - CPF          →  "***.***.***-**"
  - senha/hash   →  "***"
  - demais hits  →  primeiros 2 chars + "***"
"""
import re
from typing import Any

_SENSITIVE_KEYS = {
    "senha", "senha_hash", "password", "hash",
    "cpf", "registro_geral",
    "cartao", "card", "cvv", "numero_conta",
    "token", "secret", "api_key",
}

_CPF_RE = re.compile(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}")


def _is_sensitive(key: str) -> bool:
    key_lower = key.lower()
    return any(s in key_lower for s in _SENSITIVE_KEYS)


def _mask_value(key: str, value: Any) -> Any:
    if value is None:
        return value

    key_lower = key.lower()

    if "cpf" in key_lower:
        return "***.***.***-**"

    if any(s in key_lower for s in ("senha", "password", "hash", "token", "secret", "key")):
        return "***"

    raw = str(value)
    if len(raw) <= 2:
        return "***"
    return raw[:2] + "***"


def mask_sensitive(data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Percorre o dict recursivamente mascarando campos sensíveis."""
    if data is None:
        return None

    result: dict[str, Any] = {}
    for key, value in data.items():
        if _is_sensitive(key):
            result[key] = _mask_value(key, value)
        elif isinstance(value, dict):
            result[key] = mask_sensitive(value)
        elif isinstance(value, str):
            result[key] = _CPF_RE.sub("***.***.***-**", value)
        else:
            result[key] = value
    return result