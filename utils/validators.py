import re

def validar_username(username):
    """
    Valida y sanitiza el nombre de usuario de posibles inyecciones.
    Retorna el string limpio si es válido, lanza ValueError si no.
    """
    username = username.strip()
    
    # Exige que el largo sea prudente
    if len(username) < 3 or len(username) > 30:
        raise ValueError("El usuario debe tener entre 3 y 30 caracteres.")
        
    # Exige que solo tenga caracteres alfanuméricos y guiones
    if not re.match("^[a-zA-Z0-9_.-]+$", username):
        raise ValueError("El usuario solo puede contener letras, números, guiones y puntos.")
        
    return username

def validar_password_format(password):
    """
    Comprueba si existe alguna anomalía con la contraseña ingresada
    antes de enviarla al comprobador criptográfico.
    """
    # En esquemas reales, un límite previene Denial of Service (DoS) con hashes largos
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    
    if len(password) > 128:
        raise ValueError("La contraseña excede el límite de tamaño.")
        
    return password
