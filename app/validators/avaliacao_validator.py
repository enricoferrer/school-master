def validate_peso_positivo(v: float) -> float:
        if v <= 0:
            raise ValueError("Peso deve ser maior que zero.")
        return v