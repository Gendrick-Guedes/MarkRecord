import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el sys.path
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import tkinter as tk
from tkinter import messagebox

def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana flotante de Tkinter en medio de la pantalla calculando 
    la resolución actual del usuario y restando la mitad de las dimensiones dadas.
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    
    # Ecuación de centrado
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    
    # Aplica las medidas con la sintaxis de tkinter: "ANCHO x ALTO + X + Y"
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

class MainSelector:
    def __init__(self, current_user=None):
        self.current_user = current_user
        
        self.root = tk.Tk()
        # Fallback a string seguro
        user_role = self.current_user.get('role', 'OFFLINE') if self.current_user else 'OFFLINE'
        self.root.title(f"Sistema Integrado - Rol: {user_role.upper()}")
        centrar_ventana(self.root, 450, 400)
        self.current_app = None
        
        # Tema Global (incluye menú superior y modo oscuro persistente)
        from launcher.theme import GlobalTheme
        self.theme = GlobalTheme(self.root)
        
        self.setup_menu()
        self.root.mainloop()

    def setup_menu(self):
        # Limpiar ventana asegurándonos de no destruir la barra de tema
        for widget in self.root.winfo_children():
            if getattr(widget, "_is_theme_bar", False) or isinstance(widget, tk.Menu):
                continue
            widget.destroy()
            
        self.root.title("Selección de Aplicación")
        centrar_ventana(self.root, 450, 400)
        
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(expand=True)
        
        tk.Label(frame, text="¿A qué módulo desea entrar?", font=("Arial", 14, "bold"), pady=20).pack()
        
        tk.Button(frame, text="📚 Gestión Académica", font=("Arial", 12), width=25, height=2,
                  command=self.open_gestion, bg="#e7f1ff").pack(pady=10)
        
        user_role = self.current_user.get('role', 'offline').lower() if self.current_user else 'offline'
        if user_role == 'admin':
            tk.Button(frame, text="🔐 Encriptación / Desencriptación", font=("Arial", 12), width=25, height=2,
                      command=self.open_encryption, bg="#fff0f0").pack(pady=10)
                  
        # Botón de Cerrar Sesión
        if self.current_user:
            tk.Button(frame, text="🚪 Cerrar Sesión", font=("Arial", 12), width=25, height=2, bg="#f8d7da", command=self.root.destroy).pack(pady=10)
                  
        # Aplicamos el tema tras reconstruir el menú
        self.theme.apply()

    # =========================================================
    # Manejadores de Eventos: Carga Tardia de Modulos
    # =========================================================
    def open_gestion(self):
        # Importación tardía (Lazy Import): Solo importamos GestionAcademicaApp 
        # cuando hacemos click al botón para evitar ciclos de importación o demorar
        # el arranque del selector principal si la app falla.
        try:
            from gestion_academica.app import GestionAcademicaApp
            
            # Limpiar la ventana actual cuidando no destruir nuestra barra de preferencias
            for widget in self.root.winfo_children():
                if getattr(widget, "_is_theme_bar", False) or isinstance(widget, tk.Menu):
                    continue
                widget.destroy()
            # Pasamos la sesión directamente al Gestor
            self.current_app = GestionAcademicaApp(self.root, self.setup_menu, current_user=self.current_user)
            
            # Reaplicamos el tema a todos los widgets creados recién
            self.theme.apply()
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo abrir Gestión Académica:\n{e}")

    def open_encryption(self):
        # Importación tardía
        try:
            from encriptacion.encryption_ui import EncryptionApp
            # Limpiar y abrir encriptación asegurando el Menú
            for widget in self.root.winfo_children():
                if getattr(widget, "_is_theme_bar", False) or isinstance(widget, tk.Menu):
                    continue
                widget.destroy()
            
            # El encriptador no necesita permisos, pero igual respeta la App
            self.current_app = EncryptionApp(self.root, self.setup_menu)
            
            # Reaplicamos el tema
            self.theme.apply()
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo abrir Encriptación:\n{e}")

if __name__ == "__main__":
    MainSelector()
