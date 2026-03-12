def validate_codigo(v: str) -> str:
    v_normalized = v.strip()
    if len(v_normalized) != 4:
        raise ValueError("Código deve conter 4 caracteres")
    return v_normalized

def validate_nome(v: str) -> str:
    nome_normalized = v.strip()
    if not nome_normalized or len(nome_normalized) > 25:
        raise ValueError("Nome inválido!")
    return nome_normalized