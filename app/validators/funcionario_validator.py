def not_empty(v: str) -> str:
    if not v or not v.strip():
        raise ValueError("Valor não pode ser vazio!")
    return v.strip()

def validate_matricula(v: str) -> str:
    matricula = v.strip()
    if len(matricula) < 5:
        raise ValueError("Matricula não pode conter menos de 5 digitos")
    return matricula