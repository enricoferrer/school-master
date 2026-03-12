from datetime import date
import re

def nome_social_strip(v: str | None) -> str | None:
    if v is not None:
        return v.strip() or None
    return v

def validate_cpf(v: str) -> str:
    cpf = re.sub(r"\D", "", v)
    if len(cpf) != 11:
        raise ValueError("CPF deve conter 11 dígitos")
    if cpf == cpf[0] * 11:
        raise ValueError("CPF inválido")

    for i in range(2):
        soma = sum(int(cpf[j]) * (10 + i - j) for j in range(9 + i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[9 + i]):
            raise ValueError("CPF inválido")

    return cpf

def validate_telefone(v: str) -> str:
    telefone = re.sub(r"\D", "", v)
    if len(telefone) not in (10, 11):
        raise ValueError("Telefone deve ter 10 ou 11 dígitos")
    return telefone

def validate_data_nascimento(v: date) -> date:
    if v >= date.today():
        raise ValueError("Data de nascimento deve ser no passado")
    return v