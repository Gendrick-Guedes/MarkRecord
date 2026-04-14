import tkinter as tk
from tkinter import messagebox
import os
import sys

# Agregar path para poder importar módulos root de forma absoluta si se ejecuta este módulo directo
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from launcher.theme import apply_theme_to_widget, load_theme
from launcher.selector import centrar_ventana
from models.user_model import UserModel
from auth.security import verify_password
from utils.validators import validar_username, validar_password_format

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        # Quitar la barra tradicional y crear una ventana limpia ("moderna")
        centrar_ventana(self.root, 360, 400)
        
        self.user_model = UserModel()
        self.authenticated_user = None  # Almacenará los metadatos de sesión (incluyendo rol) una vez logrado el inicio
        
        self.dark_mode = load_theme()
        
        self.setup_ui()
        apply_theme_to_widget(self.root, self.dark_mode)

    def setup_ui(self):
        # Frame central de autenticación
        self.main_container = tk.Frame(self.root, padx=30, pady=20)
        self.main_container.pack(fill="both", expand=True)

        # Título y Diseño
        tk.Label(self.main_container, text="MarkRecord", font=("Arial", 22, "bold")).pack(pady=(20, 20))

        # Username
        tk.Label(self.main_container, text="Usuario:", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        self.entry_username = tk.Entry(self.main_container, font=("Arial", 12))
        self.entry_username.pack(fill="x", pady=(5, 15), ipady=5)
        self.entry_username.focus()

        # Password
        tk.Label(self.main_container, text="Contraseña:", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        self.entry_password = tk.Entry(self.main_container, font=("Arial", 12), show="*")
        self.entry_password.pack(fill="x", pady=(5, 20), ipady=5)
        
        # Permitir Login al presionar Enter en el password
        self.entry_password.bind("<Return>", lambda event: self.attempt_login())

        # Botón Acceder
        self.btn_login = tk.Button(self.main_container, text="INICIAR SESIÓN", font=("Arial", 11, "bold"), 
                                   bg="#0078D7", fg="white", cursor="hand2", command=self.attempt_login)
        self.btn_login.pack(fill="x", ipady=8, pady=(10, 0))
        
        # Label oculto para mensajes de error
        self.lbl_error = tk.Label(self.main_container, text="", fg="#ff5555", font=("Arial", 9))
        self.lbl_error.pack(pady=10)

    def attempt_login(self):
        username_raw = self.entry_username.get()
        password_raw = self.entry_password.get()

        # Limpiamos el texto de error previo
        self.lbl_error.config(text="")
        
        # Validación Local Temprana (Input sanitization)
        try:
            username = validar_username(username_raw)
            password = validar_password_format(password_raw)
        except ValueError as e:
            self.lbl_error.config(text=str(e))
            return
            
        # Comprobaciones de Base de Datos
        if not self.user_model.db.conn:
            self.lbl_error.config(text="❌ No se pudo conectar a la BD.")
            return

        usuario = self.user_model.get_user_by_username(username)

        # Si el usuario NO existe
        if not usuario:
            self.lbl_error.config(text="Credenciales incorrectas.")
            return
            
        # Revisamos si la cuenta está previamente bloqueada
        if usuario.get('bloqueado'):
            self.lbl_error.config(text="🚫 Cuenta bloqueada por intentos fallidos.\nContacta con soporte.")
            return

        # Verificamos hash Argon2
        if verify_password(usuario['password'], password):
            # ! Contraseña Correcta !
            self.user_model.reset_failed_attempts(username)
            self.authenticated_user = usuario
            self.root.destroy() # Cierra el ciclo de la propia ventana login devolviendo el control al main.py
        else:
            # ! Contraseña Incorrecta !
            se_bloqueo = self.user_model.increment_failed_attempts(username)
            if se_bloqueo:
                self.lbl_error.config(text="🚫 Superaste los 10 intentos. Cuenta BLOQUEADA.")
            else:
                intentos = usuario.get('intentos_fallidos', 0) + 1
                self.lbl_error.config(text=f"Credenciales incorrectas. (Intento {intentos}/10)")

def run_auth_flow():
    """Crea una ventana temporal para manejar el login y devuelve el usuario autenticado (si lo hay)"""
    auth_root = tk.Tk()
    app = LoginWindow(auth_root)
    # Hacer que la ventana maneje un evento WM_DELETE_WINDOW si la persona cierra con la 'X' para detener el sistema
    auth_root.protocol("WM_DELETE_WINDOW", sys.exit)
    auth_root.mainloop()
    
    return app.authenticated_user
