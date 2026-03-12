def not_empty(v: str) -> str:
    if not v or not v.strip():
        raise ValueError("Valor não pode ser vazio!")
    return v.strip()