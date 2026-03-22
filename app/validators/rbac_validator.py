from app.core.permissions import VALID_ROLES

def validate_roles(v: str) -> str:
    v = v.upper()
    if v not in VALID_ROLES:
        raise ValueError(f"Papel inválido. Use: {', '.join(sorted(VALID_ROLES))}")
    return v