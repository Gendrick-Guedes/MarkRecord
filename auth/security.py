from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Instanciar el hasher usando mejores prácticas de Argon2
ph = PasswordHasher()

def hash_password(password: str) -> str:
    """
    Genera un hash seguro unidireccional utilizando Argon2.
    """
    return ph.hash(password)

def verify_password(hash_str: str, plain_password: str) -> bool:
    """
    Verifica si la contraseña plana coincide con el hash encriptado.
    """
    try:
        ph.verify(hash_str, plain_password)
        
        # Opcional: ph.check_needs_rehash(hash_str) puede usarse 
        # si los parámetros de seguridad subyacente cambian con los años.
        return True
    except VerifyMismatchError:
        return False
