import json
import os
import tkinter as tk

THEME_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.json")

def load_theme():
    """Carga la preferencia de tema desde un archivo local"""
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, 'r') as f:
                data = json.load(f)
                return data.get("dark_mode", False)
    except Exception:
        pass
    return False

def save_theme(dark_mode):
    """Guarda la preferencia de tema en disco para persistencia"""
    try:
        with open(THEME_FILE, 'w') as f:
            json.dump({"dark_mode": dark_mode}, f)
    except Exception:
        pass

def is_hex_color(color_name):
    return color_name.startswith("#")

def apply_theme_to_widget(widget, dark_mode):
    """Recorre de forma recursiva aplicando los colores del Modo Oscuro/Claro"""
    
    # Paleta Oscura Ajustada (Gris muy oscuro casi negro)
    bg_dark = "#171717"
    fg_dark = "#eeeeee"
    bg_dark_input = "#1f1f1f"
    bg_dark_btn = "#333333"
    
    # Paleta Clara (Por Defecto de Tkinter/Windows)
    bg_light = "SystemButtonFace" # Default windows background
    if widget.tk.call('tk', 'windowingsystem') == 'x11':
        bg_light = "#d9d9d9"
    elif widget.tk.call('tk', 'windowingsystem') == 'aqua': # MacOS
        bg_light = "systemWindowBackgroundColor"
    
    fg_light = "#000000"
    bg_light_input = "#ffffff"

    try:
        wtype = widget.winfo_class()
        
        # Aplicamos fondos a frames e interfaces principales
        if wtype in ("Frame", "Tk", "Toplevel"):
            # Si el frame tiene un color personalizado (como #e7f1ff), puede que el usuario no quiera oscurecerlo.
            # En nuestro proyecto, la mayoría de marcos (Frames) no tienen bg forzado salvo excepciones.
            widget.configure(bg=bg_dark if dark_mode else bg_light)
            
            # MAGIA DE WINDOWS: Volver la barra de título superior oscura
            if wtype in ("Tk", "Toplevel") and widget.tk.call('tk', 'windowingsystem') == 'win32':
                try:
                    import ctypes
                    # Constante DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    hwnd = ctypes.windll.user32.GetParent(widget.winfo_id())
                    value = ctypes.c_int(2 if dark_mode else 0)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
                except Exception:
                    pass

        elif wtype == "LabelFrame":
            widget.configure(bg=bg_dark if dark_mode else bg_light, fg=fg_dark if dark_mode else fg_light)
            
        elif wtype in ("Label", "Checkbutton", "Radiobutton"):
            # Para Label encriptacion, fg suele ser '#666', ignoramos por simplicidad
            widget.configure(bg=bg_dark if dark_mode else bg_light, fg=fg_dark if dark_mode else fg_light)
            if wtype in ("Checkbutton", "Radiobutton"):
                widget.configure(selectcolor=bg_dark_input if dark_mode else bg_light_input)

        elif wtype == "Listbox":
            widget.configure(
                bg=bg_dark_input if dark_mode else bg_light_input, 
                fg=fg_dark if dark_mode else fg_light, 
                selectbackground="#555555" if dark_mode else "#0078D7", 
                selectforeground="#ffffff"
            )

        elif wtype == "Entry":
            widget.configure(
                bg=bg_dark_input if dark_mode else bg_light_input, 
                fg=fg_dark if dark_mode else fg_light, 
                insertbackground=fg_dark if dark_mode else fg_light
            )
            
        elif wtype == "Button":
            # PRECAUCIÓN: No queremos arruinar los colores "rojo no saturado", "verde caña", etc.
            # Solo aplicamos oscuro a los botones genéricos
            current_bg = widget.cget("bg")
            if "System" in current_bg or current_bg.lower() in ["#ffffff", "white", "#d9d9d9"]:
                widget.configure(bg=bg_dark_btn if dark_mode else bg_light, fg=fg_dark if dark_mode else fg_light)

    except tk.TclError:
        pass

    # Llamada recursiva a todos los hijos
    for child in widget.winfo_children():
        apply_theme_to_widget(child, dark_mode)

class GlobalTheme:
    def __init__(self, root):
        self.root = root
        self.dark_mode = tk.BooleanVar(value=load_theme())
        self.setup_menu()
        
        # Aplicamos el tema la primera vez (para el menú principal)
        self.apply()

    def setup_menu(self):
        # En lugar de un Menú nativo (que Windows no deja pintar de oscuro),
        # usamos un Frame superior persistente.
        self.top_bar = tk.Frame(self.root, bg="#171717" if self.dark_mode.get() else "SystemButtonFace")
        self.top_bar._is_theme_bar = True  # Marca para evitar que selector.py la elimine
        self.top_bar.pack(side="top", fill="x")
        
        self.theme_btn = tk.Checkbutton(
            self.top_bar, 
            text="Modo Oscuro", 
            variable=self.dark_mode, 
            command=self.toggle_and_apply,
            bg="#171717" if self.dark_mode.get() else "SystemButtonFace",
            fg="#eeeeee" if self.dark_mode.get() else "#000000",
            selectcolor="#1f1f1f" if self.dark_mode.get() else "#ffffff"
        )
        self.theme_btn.pack(side="right", padx=10, pady=2)

    def toggle_and_apply(self):
        save_theme(self.dark_mode.get())
        self.apply()

    def apply(self):
        # Ajustamos el color de la barra superior
        bg_color = "#171717" if self.dark_mode.get() else "SystemButtonFace"
        fg_color = "#eeeeee" if self.dark_mode.get() else "#000000"
        sel_color = "#1f1f1f" if self.dark_mode.get() else "#ffffff"
        
        self.top_bar.config(bg=bg_color)
        self.theme_btn.config(bg=bg_color, fg=fg_color, selectcolor=sel_color)
        
        # El tema se re-aplica a toda la ventana actual
        apply_theme_to_widget(self.root, self.dark_mode.get())
