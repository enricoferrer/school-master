"""
Gera o diff no formato exigido pela US:
  { "campo": { "de": <valor_antigo>, "para": <valor_novo> } }
"""
from typing import Any
from .sensitive_masker import mask_sensitive


def build_diff(
    antes: dict[str, Any] | None,
    depois: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Compara dois dicionários e retorna apenas os campos que mudaram.

    - POST  → antes=None, depois=payload    → retorna campos criados
    - PATCH → antes=estado_db, depois=body  → retorna campos modificados
    - DELETE→ antes=estado_db, depois=None  → retorna campos removidos
    """
    antes_safe  = mask_sensitive(antes  or {})
    depois_safe = mask_sensitive(depois or {})

    all_keys = set(antes_safe) | set(depois_safe)
    diff: dict[str, Any] = {}

    for campo in all_keys:
        val_antigo = antes_safe.get(campo)
        val_novo   = depois_safe.get(campo)
        if val_antigo != val_novo:
            diff[campo] = {"de": val_antigo, "para": val_novo}

    return diff