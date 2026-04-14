from config.db import DatabaseAuth

class UserModel:
    def __init__(self):
        self.db = DatabaseAuth()

    def get_user_by_username(self, username):
        """Busca y retorna un usuario por su nombre exacto."""
        query = "SELECT * FROM usuarios WHERE Username = %s LIMIT 1"
        res = self.db.ejecutar_consulta(query, (username,))
        return res[0] if res else None

    def increment_failed_attempts(self, username):
        """Incrementa el contador de fallos del usuario; si llega a 10 lo bloquea."""
        # Incrementar de 1 en 1
        query = "UPDATE usuarios SET Intentos_Fallidos = Intentos_Fallidos + 1 WHERE Username = %s"
        self.db.ejecutar_accion(query, (username,))
        
        # Evaluar bloqueo
        usuario = self.get_user_by_username(username)
        if usuario and usuario.get('intentos_fallidos', 0) >= 10:
            self.lock_user(username)
            return True # Retorna True indicando que acaba de ser bloqueado
        return False

    def reset_failed_attempts(self, username):
        """Restablece los fallos a 0 ante un inicio de sesión exitoso."""
        query = "UPDATE usuarios SET Intentos_Fallidos = 0 WHERE Username = %s"
        return self.db.ejecutar_accion(query, (username,))

    def lock_user(self, username):
        """Bloquea manualmente un usuario."""
        query = "UPDATE usuarios SET Bloqueado = 1 WHERE Username = %s"
        return self.db.ejecutar_accion(query, (username,))
