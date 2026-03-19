from datetime import date


def validate_data_matricula(v: date) -> date:
    if v > date.today():
        raise ValueError("Data de matricula deve ser no passado")
    if not v:
        raise ValueError("Data de matricula deve ser preenchida!")
    return v

def validate_matricula(v: str) -> str:
    matricula_formatada = v.strip()
    if len(matricula_formatada) > 10:
        raise ValueError("Matricula deve contar no maximo 10 caracteres")
    return matricula_formatada