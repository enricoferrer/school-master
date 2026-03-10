def validate_carga_horaria(v: int) -> int:
    if not v or v > 44:
        raise ValueError(f"Carga horaria de '{v}' é inválida!")
    return v