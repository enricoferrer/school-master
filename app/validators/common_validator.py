from datetime import date

def not_empty(v: str) -> str:
    if not v or not v.strip():
        raise ValueError("Valor não pode ser vazio!")
    return v.strip()

def data_nao_futura(v: date) -> date:
    if v > date.today():
        raise ValueError("Data não pode ser futura!")
    return v