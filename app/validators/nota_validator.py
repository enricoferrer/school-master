def validate_valor_nota_valido(v: float)-> float:
        if not (float("0") <= v <= float("10")):
            raise ValueError("Nota deve estar entre 0 e 10.")
        return v