import tkinter as tk
from tkinter import filedialog, messagebox
import os
from encriptacion.cipher_logic import FileCipher

# Importar función de centrado centralizada
from launcher.selector import centrar_ventana

class EncryptionApp:
    def __init__(self, root, on_back_callback):
        self.root = root
        self.root.title("Encriptación / Desencriptación")
        centrar_ventana(self.root, 650, 600)
        self.on_back = on_back_callback
        self.cipher = FileCipher()
        
        self.selected_file = ""
        self.output_path = ""
        self.current_key = None
        
        self.setup_ui()

    def setup_ui(self):
        # Frame principal con scroll si es necesario
        self.main_frame = tk.Frame(self.root, padx=20, pady=10)
        self.main_frame.pack(fill="both", expand=True)

        # Botón Volver
        tk.Button(self.main_frame, text="← Volver al inicio", command=self.on_back, font=("Arial", 10)).pack(anchor="nw")

        tk.Label(self.main_frame, text="Seguridad de Archivos Locales", font=("Arial", 16, "bold"), pady=5).pack()
        tk.Label(self.main_frame, text="Criptografía AES-256 (Fernet)", font=("Arial", 9, "italic"), fg="gray").pack()

        # --- SECCIÓN DE LLAVE (KEY) ---
        key_frame = tk.LabelFrame(self.main_frame, text="Gestión de Llave (.key)", padx=10, pady=10)
        key_frame.pack(fill="x", pady=10)

        self.key_status_label = tk.Label(key_frame, text="❌ Sin llave cargada", fg="red", font=("Arial", 10, "bold"))
        self.key_status_label.pack(side="top", anchor="w")

        key_buttons = tk.Frame(key_frame)
        key_buttons.pack(fill="x", pady=5)

        tk.Button(key_buttons, text="🆕 Generar Nueva Llave", command=self.generate_key, bg="#e7f1ff").pack(side="left", padx=5)
        tk.Button(key_buttons, text="📂 Cargar Llave Existente", command=self.load_key_file).pack(side="left", padx=5)

        # --- SECCIÓN DE ARCHIVO ---
        file_frame = tk.LabelFrame(self.main_frame, text="Selección de Archivo", padx=10, pady=10)
        file_frame.pack(fill="x", pady=10)
        
        self.file_label = tk.Label(file_frame, text="Ningún archivo seleccionado", wraplength=550, justify="left")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(file_frame, text="🔍 Buscar Archivo", command=self.select_file).pack(side="right")

        # --- SECCIÓN DE DESTINO ---
        # Permite seleccionar en dónde guardar el archivo encriptado resultante
        dest_frame = tk.LabelFrame(self.main_frame, text="Ruta de Salida", padx=10, pady=10)
        dest_frame.pack(fill="x", pady=10)
        
        self.dest_label = tk.Label(dest_frame, text="Por defecto: misma carpeta del archivo", wraplength=550, justify="left")
        self.dest_label.pack(side="left", fill="x", expand=True)
        
        tk.Button(dest_frame, text="📁 Cambiar Destino", command=self.select_dest).pack(side="right")

        # --- BOTONES DE ACCIÓN ---
        # Controlan los métodos del cipher_logic dependiendo del botón presionado
        action_frame = tk.Frame(self.main_frame, pady=15)
        action_frame.pack()
        
        self.btn_encrypt = tk.Button(action_frame, text="🔐 Encriptar", command=self.encrypt, 
                                   font=("Arial", 12, "bold"), width=15, bg="#d4edda", state="disabled")
        self.btn_encrypt.pack(side="left", padx=10)
        
        self.btn_decrypt = tk.Button(action_frame, text="🔓 Desencriptar", command=self.decrypt, 
                                   font=("Arial", 12, "bold"), width=15, bg="#f8d7da", state="disabled")
        self.btn_decrypt.pack(side="left", padx=10)

        # Notas de ayuda
        help_text = (
            "💡 Instrucciones:\n"
            "1. Selecciona el archivo que quieres proteger o recuperar.\n"
            "2. Genera una llave nueva (se llamará automáticamente como el archivo) o carga una que ya tengas.\n"
            "3. Presiona Encriptar o Desencriptar.\n"
            "⚠️ ¡OJO! Si pierdes la llave (.key), no podrás recuperar tus archivos."
        )
        tk.Label(self.main_frame, text=help_text, justify="left", fg="#666", font=("Arial", 9)).pack(pady=10)

    def generate_key(self):
        if not self.selected_file:
            messagebox.showwarning("Atención", "Selecciona primero el archivo para el cual deseas generar la llave.")
            return

        try:
            new_key = self.cipher.generate_new_key()
            
            # Sugerir nombre basado en el archivo seleccionado
            nombre_base = os.path.basename(self.selected_file)
            sugerencia_nombre = f"Key_{nombre_base}.key" # Añadimos .key explícitamente a la sugerencia
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".key",
                filetypes=[("Key files", "*.key")],
                title="Guardar nueva llave como...",
                initialfile=sugerencia_nombre
            )
            
            if file_path:
                # Asegurar que tenga la extensión .key por si el usuario la borró en el diálogo
                if not file_path.lower().endswith(".key"):
                    file_path += ".key"
                    
                with open(file_path, "wb") as f:
                    f.write(new_key)
                self.load_key_from_data(new_key, os.path.basename(file_path))
                messagebox.showinfo("Éxito", f"Llave generada y guardada en:\n{file_path}\n\nGuárdala bien, es la única forma de desencriptar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la llave: {e}")

    def load_key_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Key files", "*.key")],
            title="Seleccionar archivo de llave"
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    key_data = f.read()
                if self.cipher.set_key(key_data):
                    self.load_key_from_data(key_data, os.path.basename(file_path))
                else:
                    raise Exception("El archivo seleccionado no es una llave válida.")
            except Exception as e:
                messagebox.showerror("Error de Llave", str(e))

    def load_key_from_data(self, key_data, name):
        self.current_key = key_data
        self.cipher.set_key(key_data)
        self.key_status_label.config(text=f"✅ Llave cargada: {name}", fg="green")
        self.btn_encrypt.config(state="normal")
        self.btn_decrypt.config(state="normal")

    def select_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.selected_file = file
            self.file_label.config(text=f"Archivo: {os.path.basename(file)}")
            self.output_path = os.path.dirname(file)
            self.dest_label.config(text=f"Destino: {self.output_path}")

    def select_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_path = folder
            self.dest_label.config(text=f"Destino: {self.output_path}")

    def encrypt(self):
        if not self.selected_file:
            messagebox.showwarning("Atención", "Selecciona un archivo primero")
            return
        try:
            res = self.cipher.encrypt_file(self.selected_file, self.output_path)
            messagebox.showinfo("Éxito", f"Archivo encriptado correctamente.\n\nResultado:\n{os.path.basename(res)}\n\nUbicación:\n{os.path.dirname(res)}")
        except Exception as e:
            messagebox.showerror("Error de Encriptación", str(e))

    def decrypt(self):
        if not self.selected_file:
            messagebox.showwarning("Atención", "Selecciona un archivo primero")
            return
        try:
            res = self.cipher.decrypt_file(self.selected_file, self.output_path)
            messagebox.showinfo("Éxito", f"Archivo desencriptado correctamente.\n\nResultado:\n{os.path.basename(res)}\n\nUbicación:\n{os.path.dirname(res)}")
        except Exception as e:
            messagebox.showerror("Error de Desencriptación", str(e))
