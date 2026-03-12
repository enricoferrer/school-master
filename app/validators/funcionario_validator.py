def validate_matricula(v: str) -> str:
    matricula = v.strip()
    if len(matricula) < 5:
        raise ValueError("Matricula não pode conter menos de 5 digitos")
    return matricula