import os
import sys
import tkinter as tk
from tkinter import messagebox
from launcher.theme import load_theme, apply_theme_to_widget

# =========================
# Configuración de Rutas (Asegura que el programa encuentre sus carpetas)
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

#==========================
# Imports de módulos
#==========================

# Importa el manejo de datos (json + mysql)
from gestion_academica.data.data_manager import data, cargar, guardar

# Importar función de centrado desde el selector si es posible
try:
    from launcher.selector import centrar_ventana
except ImportError:
    def centrar_ventana(ventana, ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto  = ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto  // 2) - (alto  // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# Importa funciones para actualizar las listas en la interfaz
from gestion_academica.ui.ui_listas import actualizar_asignaturas, actualizar_grupos, actualizar_estudiantes

# Importa funciones crud (crear, eliminar, etc.)
try:
    from gestion_academica.controllers.crud import (
        agregar_asignatura,
        eliminar_asignatura,
        agregar_grupo,
        eliminar_grupo,
        agregar_estudiante,
        eliminar_estudiante
    )
except ImportError:
    from gestion_academica.controllers.crud import (
        agregar_asignatura,
        eliminar_asignatura,
        agregar_grupo,
        eliminar_grupo
    )
    from gestion_academica.controllers.crud import agregar_estudiante, eliminar_estudiante

# Importa ventana de edición
from gestion_academica.ui.editor import editar

# Importa generador automático de datos
from gestion_academica.ui.generador import generar_datos

# Importa sincronización con base de datos
from gestion_academica.services.cloud_sync import CloudSync

# Importa configuración por defecto
from gestion_academica.models.notas import DEFAULT_CONFIG

#==========================
# Eventos
#==========================

# Función para alternar el checkbox al hacer clic
def toggle_checkbox(event):
    lb = event.widget
    index = lb.nearest(event.y)
    if index < 0:
        return

    # Solo toggles si se hace clic en los primeros caracteres (el "cuadro")
    # Aproximadamente los primeros 30 píxeles
    if event.x < 30:
        current_text = lb.get(index)
        if current_text.startswith("[ ]"):
            new_text = "[x]" + current_text[3:]
        else:
            new_text = "[ ]" + current_text[3:]

        # Guardamos la selección actual para restaurarla después de la edición
        current_selection = lb.curselection()

        lb.delete(index)
        lb.insert(index, new_text)

        # Restauramos la selección si el elemento toggleado era el seleccionado
        if current_selection and current_selection[0] == index:
            lb.select_set(index)

        return "break"

#==========================
# Interfaz principal
#==========================

class GestionAcademicaApp:
    def __init__(self, root, on_back_callback, current_user=None):
        self.root = root
        self.root.title("Gestión Académica Profesional")
        centrar_ventana(self.root, 1024, 650)
        self.on_back = on_back_callback
        self.current_user = current_user

        # Tamaño inicial de fuente de las listas (Utilizado para el Zoom)
        self.font_size = 10

        # Carga los datos desde json al iniciar
        cargar()

        self.setup_ui()

    def on_zoom(self, event):
        # Aumentar o disminuir fuente basado en la rueda del ratón
        if event.delta > 0:
            self.font_size += 1
        else:
            self.font_size -= 1

        # Límites de Zoom razonables
        if self.font_size < 6:  self.font_size = 6
        if self.font_size > 28: self.font_size = 28

        nueva_fuente = ("Consolas", self.font_size)
        self.lista_asignaturas.config(font=nueva_fuente)
        self.lista_grupos.config(font=nueva_fuente)
        self.lista_estudiantes.config(font=nueva_fuente)

    def toggle_all(self, lb, check):
        """Selecciona o deselecciona todos los elementos de un panel"""
        for i in range(lb.size()):
            current_text = lb.get(i)
            if check and current_text.startswith("[ ]"):
                lb.delete(i)
                lb.insert(i, "[x]" + current_text[3:])
            elif not check and current_text.startswith("[x]"):
                lb.delete(i)
                lb.insert(i, "[ ]" + current_text[3:])

    # ======================================================
    # Ventana de Estructura Calificativa
    # ======================================================
    def abrir_estructura_calificativa(self):
        """
        Abre una ventana modal para modificar los porcentajes por componente,
        los límites de cantidad de notas y el total de clases de asistencia.
        Solo visible para profesor, coordinador, director y admin.
        """
        config = data.get("__config__", DEFAULT_CONFIG)
        pesos   = config.get("pesos",   DEFAULT_CONFIG["pesos"])
        limites = config.get("limites", DEFAULT_CONFIG["limites"])
        asis_total = config.get("asistencia_total", DEFAULT_CONFIG["asistencia_total"])

        dark = load_theme()

        win = tk.Toplevel(self.root)
        win.title("Estructura Calificativa")
        try:
            centrar_ventana(win, 480, 580)
        except Exception:
            win.geometry("480x580")
        win.grab_set()
        win.transient(self.root)
        win.focus_set()
        win.resizable(False, False)

        # ---- Título ----
        tk.Label(win, text="Estructura Calificativa", font=("Arial", 13, "bold")).pack(pady=(12, 4))
        tk.Label(win, text="Los porcentajes deben sumar exactamente 100%", font=("Arial", 9), fg="#888").pack()

        # ---- Frame de porcentajes ----
        frame_pesos = tk.LabelFrame(win, text="Porcentajes", font=("Arial", 10, "bold"), padx=10, pady=8)
        frame_pesos.pack(fill="x", padx=20, pady=(10, 4))

        campos_pesos = {}
        componentes = [
            ("final",        "Examen Semestral"),
            ("parciales",    "Parciales"),
            ("labs",         "Laboratorios"),
            ("asignaciones", "Asignaciones / Tareas"),
            ("portafolio",   "Portafolio"),
            ("asistencia",   "Asistencia"),
        ]
        for i, (key, label) in enumerate(componentes):
            tk.Label(frame_pesos, text=f"{label}:", width=22, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=str(pesos.get(key, DEFAULT_CONFIG["pesos"][key])))
            e = tk.Entry(frame_pesos, textvariable=var, width=8, justify="center")
            e.grid(row=i, column=1, padx=5, pady=2)
            tk.Label(frame_pesos, text="%").grid(row=i, column=2, sticky="w")
            campos_pesos[key] = var

        # ---- Frame de límites de notas ----
        frame_lim = tk.LabelFrame(win, text="Cantidad máxima de notas", font=("Arial", 10, "bold"), padx=10, pady=8)
        frame_lim.pack(fill="x", padx=20, pady=(4, 4))

        campos_lim = {}
        componentes_lim = [
            ("parciales",    "Máx. parciales"),
            ("labs",         "Máx. laboratorios"),
            ("asignaciones", "Máx. asignaciones"),
        ]
        for i, (key, label) in enumerate(componentes_lim):
            tk.Label(frame_lim, text=f"{label}:", width=22, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=str(limites.get(key, DEFAULT_CONFIG["limites"][key])))
            e = tk.Entry(frame_lim, textvariable=var, width=8, justify="center")
            e.grid(row=i, column=1, padx=5, pady=2)
            campos_lim[key] = var

        # ---- Asistencia total ----
        frame_asis = tk.LabelFrame(win, text="Asistencia", font=("Arial", 10, "bold"), padx=10, pady=8)
        frame_asis.pack(fill="x", padx=20, pady=(4, 10))

        tk.Label(frame_asis, text="Total de clases en el período:", width=26, anchor="w").grid(row=0, column=0, sticky="w", pady=2)
        var_asis = tk.StringVar(value=str(asis_total))
        tk.Entry(frame_asis, textvariable=var_asis, width=8, justify="center").grid(row=0, column=1, padx=5, pady=2)
        tk.Label(frame_asis, text="clases").grid(row=0, column=2, sticky="w")

        # ---- Botón Guardar ----
        def guardar_config():
            try:
                # -- Validar y leer pesos --
                nuevos_pesos = {}
                for key, var in campos_pesos.items():
                    val = var.get().strip()
                    try:
                        n = int(val)
                    except ValueError:
                        raise ValueError(f"El valor de '{key}' no es un número entero válido.")
                    if n < 0:
                        raise ValueError(f"El porcentaje de '{key}' no puede ser negativo.")
                    nuevos_pesos[key] = n

                # Validación especial reglamentaria para el semestral
                if nuevos_pesos.get("final", 0) < 33:
                    messagebox.showerror(
                        "Restricción Reglamentaria",
                        "Por motivos reglamentarios de la institución el porcentaje del semestral "
                        "no debe disminuir por debajo del 33%.",
                        parent=win
                    )
                    return

                total_pesos = sum(nuevos_pesos.values())
                if total_pesos != 100:
                    if total_pesos > 100:
                        raise ValueError(
                            f"El porcentaje de notas no puede superar el 100%.\n"
                            f"Actualmente suman: {total_pesos}%. Debes reducir {total_pesos - 100}%."
                        )
                    else:
                        raise ValueError(
                            f"El porcentaje de notas no puede ser menor al 100%.\n"
                            f"Actualmente suman: {total_pesos}%. Te faltan {100 - total_pesos}%."
                        )

                # -- Validar y leer límites --
                nuevos_limites = {}
                for key, var in campos_lim.items():
                    val = var.get().strip()
                    label_legible = {"parciales": "Parciales", "labs": "Laboratorios", "asignaciones": "Asignaciones"}[key]
                    try:
                        n = int(val)
                    except ValueError:
                        raise ValueError(f"El límite de {label_legible} no es un número entero válido.")
                    if n <= 0:
                        raise ValueError(f"El límite de {label_legible} debe ser mayor que 0.")
                    if n > 50:
                        raise ValueError(f"El límite de {label_legible} no puede ser mayor a 50.")
                    nuevos_limites[key] = n

                # -- Validar asistencia total --
                try:
                    asis_val = int(var_asis.get().strip())
                except ValueError:
                    raise ValueError("El total de clases de asistencia debe ser un número entero.")
                if asis_val < 1:
                    raise ValueError("El total de clases de asistencia debe ser al menos 1.")
                if asis_val > 100:
                    raise ValueError(
                        "Solo se permite ingresar hasta 100 clases en el período de asistencia."
                    )

                # -- Guardar en data y persistir --
                data["__config__"] = {
                    "pesos":            nuevos_pesos,
                    "limites":          nuevos_limites,
                    "asistencia_total": asis_val
                }
                guardar()

                # Refrescar la lista de estudiantes con los nuevos pesos
                actualizar_estudiantes(
                    self.lista_estudiantes,
                    self.lista_asignaturas,
                    self.lista_grupos,
                    data,
                    self.puede_sel_est
                )

                messagebox.showinfo("Éxito", "¡Estructura calificativa guardada correctamente!", parent=win)
                win.destroy()

            except ValueError as err:
                messagebox.showerror("Error de configuración", str(err), parent=win)

        tk.Button(
            win, text="💾  Guardar Estructura", command=guardar_config,
            bg="#c8e6c9", font=("Arial", 11, "bold"), height=2, width=26
        ).pack(pady=8)

        tk.Button(
            win, text="Cancelar", command=win.destroy,
            bg="#f8d7da", width=16
        ).pack(pady=2)

        # Aplica el tema activo (oscuro o claro) a toda la ventana de configuración
        apply_theme_to_widget(win, dark)

    # ======================================================
    # Creación de la interfaz principal
    # ======================================================
    def setup_ui(self):
        # Frame principal
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # --- Barra superior (Volver + Estructura calificativa) ---
        barra_top = tk.Frame(self.main_container)
        barra_top.pack(fill="x", padx=10, pady=5)

        tk.Button(barra_top, text="← Volver al menú", command=self.on_back).pack(side="left")

        rol = self.current_user.get('role', 'estudiante').lower() if self.current_user else 'estudiante'

        # El botón solo aparece para roles ≥ profesor
        if rol in ["admin", "director", "coordinador", "profesor"]:
            tk.Button(
                barra_top,
                text="⚙  Estructura Calificativa",
                command=self.abrir_estructura_calificativa,
                bg="#d1ecf1",
                font=("Arial", 9, "bold")
            ).pack(side="right")

        # Frame que contiene las listas
        self.frame_listas = tk.Frame(self.main_container)
        self.frame_listas.pack(fill="both", expand=True, padx=10, pady=10)

        # Checkboxes [ ] y botones Seleccionar/Deseleccionar por sección
        self.puede_sel_asig = rol in ['admin', 'director']                            # Solo Admin y Director
        self.puede_sel_grp  = rol in ['admin', 'director', 'coordinador']             # + Coordinador
        self.puede_sel_est  = rol in ['admin', 'director', 'coordinador', 'profesor'] # + Profesor

        # Crea las tres listas principales con sus permisos de selección
        self.lista_asignaturas = self.crear_lista(self.frame_listas, "Asignaturas", self.puede_sel_asig)
        self.lista_grupos      = self.crear_lista(self.frame_listas, "Grupos",      self.puede_sel_grp)
        self.lista_estudiantes = self.crear_lista(self.frame_listas, "Estudiantes", self.puede_sel_est)

        # Eventos de selección
        self.lista_asignaturas.bind("<<ListboxSelect>>", self.seleccionar_asignatura)
        self.lista_grupos.bind("<<ListboxSelect>>", self.seleccionar_grupo)

        # Panel de botones
        self.panel_botones = tk.Frame(self.main_container)
        self.panel_botones.pack(pady=20)

        #==========================
        # Construcción de botones
        # ==========================
        btn_add_asig = tk.Button(self.panel_botones, text="Añadir Asignatura", width=15, bg="#c8e6c9",
                  command=lambda: agregar_asignatura(data, guardar, lambda: actualizar_asignaturas(self.lista_asignaturas, data, self.puede_sel_asig)))

        btn_del_asig = tk.Button(self.panel_botones, text="Eliminar Asignatura", width=15, bg="#f8d7da",
                  command=lambda: eliminar_asignatura(data, guardar, self.lista_asignaturas, self.lista_grupos, self.lista_estudiantes,
                                                      lambda: actualizar_asignaturas(self.lista_asignaturas, data, self.puede_sel_asig)))

        btn_add_grp = tk.Button(self.panel_botones, text="Añadir Grupo", width=15, bg="#c8e6c9",
                  command=lambda: agregar_grupo(data, guardar, self.lista_asignaturas,
                                               lambda: actualizar_grupos(self.lista_grupos, self.lista_asignaturas, data, self.puede_sel_grp)))

        btn_del_grp = tk.Button(self.panel_botones, text="Eliminar Grupo", width=15, bg="#f8d7da",
                  command=lambda: eliminar_grupo(data, guardar, self.lista_asignaturas, self.lista_grupos, self.lista_estudiantes,
                                                lambda: actualizar_grupos(self.lista_grupos, self.lista_asignaturas, data, self.puede_sel_grp)))

        btn_add_est = tk.Button(self.panel_botones, text="Añadir Estudiante", width=15, bg="#c8e6c9",
                  command=lambda: agregar_estudiante(data, guardar, self.lista_asignaturas, self.lista_grupos,
                                                    lambda: actualizar_estudiantes(self.lista_estudiantes, self.lista_asignaturas, self.lista_grupos, data, self.puede_sel_est)))

        btn_del_est = tk.Button(self.panel_botones, text="Eliminar Estudiante", width=15, bg="#f8d7da",
                  command=lambda: eliminar_estudiante(data, guardar, self.lista_asignaturas, self.lista_grupos, self.lista_estudiantes,
                                                     lambda: actualizar_estudiantes(self.lista_estudiantes, self.lista_asignaturas, self.lista_grupos, data, self.puede_sel_est)))

        btn_edit = tk.Button(self.panel_botones, text="Editar Campo", width=15, bg="#ffeeba",
                  command=lambda: editar(data, guardar, self.lista_asignaturas, self.lista_grupos, self.lista_estudiantes,
                                        lambda: actualizar_estudiantes(self.lista_estudiantes, self.lista_asignaturas, self.lista_grupos, data, self.puede_sel_est), self.current_user))

        btn_ver_notas = tk.Button(self.panel_botones, text="Ver nota de estudiante", width=25, bg="#e2e3e5",
                  command=lambda: editar(data, guardar, self.lista_asignaturas, self.lista_grupos, self.lista_estudiantes,
                                        lambda: actualizar_estudiantes(self.lista_estudiantes, self.lista_asignaturas, self.lista_grupos, data, self.puede_sel_est), self.current_user))

        btn_gen = tk.Button(self.panel_botones, text="Generar Datos", width=15, bg="#d1ecf1",
                  command=lambda: generar_datos(data, guardar, lambda: actualizar_asignaturas(self.lista_asignaturas, data, self.puede_sel_asig)))

        # ---------------------------------------------------------
        # Jerarquía de roles y visibilidad de botones:
        # ---------------------------------------------------------

        # Asignaturas: Admin y Director
        if rol in ["admin", "director"]:
            btn_add_asig.grid(row=0, column=0, padx=5, pady=2)
            btn_del_asig.grid(row=1, column=0, padx=5, pady=2)

        # Grupos: Admin, Director, Coordinador
        if rol in ["admin", "director", "coordinador"]:
            btn_add_grp.grid(row=0, column=1, padx=5, pady=2)
            btn_del_grp.grid(row=1, column=1, padx=5, pady=2)

        # Estudiantes: Admin, Director, Coordinador, Profesor
        if rol in ["admin", "director", "coordinador", "profesor"]:
            btn_add_est.grid(row=0, column=2, padx=5, pady=2)
            btn_del_est.grid(row=1, column=2, padx=5, pady=2)
            btn_edit.grid(row=0, column=3, padx=5, pady=2)

        # Generar Datos: solo Admin
        if rol == "admin":
            btn_gen.grid(row=1, column=3, padx=5, pady=2)

        # Ver notas (solo lectura): solo Estudiante
        if rol == "estudiante":
            btn_ver_notas.grid(row=0, column=0, padx=5, pady=2)

        # Inicializar lista
        actualizar_asignaturas(self.lista_asignaturas, data, self.puede_sel_asig)

    def crear_lista(self, parent, titulo, puede_seleccionar=True):
        """
        Crea una lista con o sin checkboxes y botones de selección múltiple según el rol.
        puede_seleccionar=True  → muestra los checkboxes [ ] y los botones Seleccionar/Deseleccionar.
        puede_seleccionar=False → lista de solo lectura visual (sin check interactivo).
        """
        f = tk.Frame(parent)
        f.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(f, text=titulo, font=("Arial", 10, "bold")).pack(pady=2)

        # Frame reservado para los botones de selección múltiple
        btn_frame = tk.Frame(f)
        btn_frame.pack(fill="x", pady=2)

        # Frame extra para contener Lista y Scrollbar juntos de manera correcta
        list_container = tk.Frame(f)
        list_container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")

        lb = tk.Listbox(list_container, selectmode="browse", exportselection=False, font=("Consolas", self.font_size))
        lb.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)
        lb.pack(side="left", fill="both", expand=True)

        if puede_seleccionar:
            # Botones de selección múltiple (solo si el rol tiene permiso en esta sección)
            tk.Button(btn_frame, text="Seleccionar Todos", font=("Arial", 8), bg="#d4edda",
                      command=lambda l=lb: self.toggle_all(l, True)).pack(side="left", fill="x", expand=True, padx=1)
            tk.Button(btn_frame, text="Deseleccionar Todos", font=("Arial", 8), bg="#f8d7da",
                      command=lambda l=lb: self.toggle_all(l, False)).pack(side="left", fill="x", expand=True, padx=1)
            # Bind del checkbox [ ] / [x] interactivo
            lb.bind("<Button-1>", toggle_checkbox)

        # Zoom siempre disponible
        lb.bind("<Control-MouseWheel>", self.on_zoom)

        return lb

    def seleccionar_asignatura(self, event):
        actualizar_grupos(self.lista_grupos, self.lista_asignaturas, data, self.puede_sel_grp)
        self.lista_estudiantes.delete(0, tk.END)

    def seleccionar_grupo(self, event):
        actualizar_estudiantes(self.lista_estudiantes, self.lista_asignaturas, self.lista_grupos, data, self.puede_sel_est)

if __name__ == "__main__":
    # Si se intenta ejecutar este archivo directamente, intentamos cargar el selector principal
    try:
        from launcher.selector import MainSelector
        MainSelector()
    except ImportError:
        # Si no se encuentra el selector (por problemas de ruta), iniciamos solo este módulo
        ventana = tk.Tk()
        app = GestionAcademicaApp(ventana, lambda: ventana.destroy())
        ventana.mainloop()