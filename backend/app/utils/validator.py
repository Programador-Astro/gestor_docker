import re
from email_validator import validate_email, EmailNotValidError
def validar_dado(dado: str, tipo: str) -> bool:
    tipo = tipo.lower()

    if tipo == 'email':
        try:
            validate_email(dado)
            return True
        except  EmailNotValidError:
            return False
    elif tipo == 'senha':
        if len(dado) <= 8:
            return False
        if not re.search(r'[A-Za-z]', dado):
            return False
        if not re.search(r'\d', dado):
            return False
        if re.search(r'[^A-Za-z0-9@!#]', dado):  # Só permite letras, números e @!#
            return False
        return True

    else:
        raise ValueError(f"Tipo de dado '{tipo}' não suportado.")