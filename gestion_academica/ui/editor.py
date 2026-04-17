import tkinter as tk
from tkinter import messagebox
from gestion_academica.ui.ui_listas import limpiar_nombre
from gestion_academica.models.notas import DEFAULT_CONFIG
from launcher.theme import load_theme, apply_theme_to_widget


# =========================
# Función principal de edición
# =========================
def editar(data, guardar, lista_asignaturas, lista_grupos, lista_estudiantes, actualizar_estudiantes, current_user=None):

    rol = current_user.get('role', 'estudiante').lower() if current_user else 'estudiante'

    # Leer configuración activa
    config = data.get("__config__", DEFAULT_CONFIG)
    pesos   = config.get("pesos",   DEFAULT_CONFIG["pesos"])
    limites = config.get("limites", DEFAULT_CONFIG["limites"])
    asis_total = config.get("asistencia_total", DEFAULT_CONFIG["asistencia_total"])

    # =========================
    # Obtener selección actual
    # =========================
    sel_a = lista_asignaturas.curselection()
    sel_g = lista_grupos.curselection()
    sel_e = lista_estudiantes.curselection()

    if rol == 'estudiante':
        if not (sel_a and sel_g and sel_e):
            messagebox.showwarning("Información", "Por favor seleccione un estudiante para ver sus notas.")
            return

    # =========================
    # Editar asignatura
    # =========================
    if sel_a and not sel_g:

        # Solo Admin y Director pueden editar el nombre de una asignatura
        if rol not in ['admin', 'director']:
            messagebox.showwarning("Permisos Insuficientes", "Solo el administrador y el director pueden editar asignaturas.")
            return

        # Obtiene asignatura seleccionada usando limpiar_nombre
        a_display = lista_asignaturas.get(sel_a[0])
        a = limpiar_nombre(a_display)

        # Solicita nuevo nombre
        nuevo = tk.simpledialog.askstring("Editar", "Nuevo nombre:", initialvalue=a)

        # Si el usuario ingresó algo, actualiza
        if nuevo:
            data[nuevo] = data.pop(a)
            guardar()

    # =========================
    # Editar grupo
    # =========================
    elif sel_a and sel_g and not sel_e:

        # Solo Admin, Director y Coordinador pueden editar el nombre de un grupo
        if rol not in ['admin', 'director', 'coordinador']:
            messagebox.showwarning("Permisos Insuficientes", "Solo el coordinador o superior puede editar grupos.")
            return

        # Obtiene asignatura y grupo usando limpiar_nombre
        a_display = lista_asignaturas.get(sel_a[0])
        g_display = lista_grupos.get(sel_g[0])

        a = limpiar_nombre(a_display)
        g = limpiar_nombre(g_display)

        # Solicita nuevo nombre de grupo
        nuevo = tk.simpledialog.askstring("Editar", "Nuevo nombre grupo:", initialvalue=g)

        # Si el usuario ingresó algo, actualiza
        if nuevo:
            data[a][nuevo] = data[a].pop(g)
            guardar()

    # =========================
    # Editar / Ver estudiante
    # =========================
    elif sel_a and sel_g and sel_e:

        # Obtiene datos del estudiante seleccionado usando limpiar_nombre
        a_display = lista_asignaturas.get(sel_a[0])
        g_display = lista_grupos.get(sel_g[0])

        a = limpiar_nombre(a_display)
        g = limpiar_nombre(g_display)
        est = data[a][g][sel_e[0]]
        notas = est["notas"]

        # =========================
        # Crear ventana de edición interactiva
        # =========================
        v = tk.Toplevel()
        v.title(f"{'Notas de' if rol == 'estudiante' else 'Editando'}: {est['nombre']}")

        # Centrar asegurando que no se mueva a una esquina remota
        try:
            from launcher.selector import centrar_ventana
            centrar_ventana(v, 430, 580)
        except ImportError:
            v.geometry("430x580")

        # Hace que esta ventana secundaria sea modal
        v.grab_set()
        v.transient(v.master)
        v.focus_set()

        # =========================
        # Función para crear campos de entrada con auto-puntuación
        # =========================
        def crear_campo(label, valor, es_lista=False, disabled=False):
            tk.Label(v, text=label, font=("Arial", 10, "bold")).pack()
            e = tk.Entry(v, width=40)
            e.insert(0, valor)

            if disabled:
                e.config(state="readonly")

            e.pack(pady=2)

            if es_lista and not disabled:
                # Evento para poner coma automática después de 2 dígitos
                def auto_coma(event):
                    if event.keysym == "BackSpace":
                        return
                    content = e.get()
                    if len(content) >= 2:
                        last_part = content.split(",")[-1].strip()
                        if len(last_part) == 2 and last_part.isdigit():
                            e.insert(tk.END, ",")

                e.bind("<KeyRelease>", auto_coma)

            return e

        # =========================
        # Campos de edición (Con restricciones de ROL)
        # =========================

        bloquear_nombre = (rol == 'estudiante')
        bloquear_notas  = (rol == 'estudiante')

        # Campo nombre
        entry_nombre = crear_campo("Nombre Estudiante", est["nombre"], disabled=bloquear_nombre)

        # Campo parciales con % dinámico
        e_parciales = crear_campo(
            f"Parciales - {pesos.get('parciales', 30)}%  (máx. {limites.get('parciales', 3)} notas)",
            ",".join(str(int(x)) for x in notas.get("parciales", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo labs con % dinámico
        e_labs = crear_campo(
            f"Laboratorios - {pesos.get('labs', 17)}%  (máx. {limites.get('labs', 10)} notas)",
            ",".join(str(int(x)) for x in notas.get("labs", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo asignaciones con % dinámico
        e_asig = crear_campo(
            f"Asignaciones - {pesos.get('asignaciones', 10)}%  (máx. {limites.get('asignaciones', 10)} notas)",
            ",".join(str(int(x)) for x in notas.get("asignaciones", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo portafolio con % dinámico
        e_port = crear_campo(
            f"Portafolio - {pesos.get('portafolio', 5)}%",
            str(int(notas.get('portafolio', 0))),
            disabled=bloquear_notas
        )

        # Campo asistencia con % dinámico y total de clases
        asis_val = notas.get("asistencia", 0)
        if isinstance(asis_val, list):
            asis_val = int(sum(asis_val) / len(asis_val)) if asis_val else 0

        e_asis = crear_campo(
            f"Asistencia - {pesos.get('asistencia', 5)}%  (clases asistidas de {asis_total})",
            str(int(asis_val)),
            disabled=bloquear_notas
        )

        # Campo semestral con % dinámico
        e_semestral = crear_campo(
            f"Examen Semestral - {pesos.get('final', 33)}%",
            str(int(notas.get('final', 0))),
            disabled=bloquear_notas
        )

        # Aplica el tema activo (oscuro o claro) a la ventana del editor
        apply_theme_to_widget(v, load_theme())

        # =========================
        # Guardar cambios del estudiante
        # =========================
        def guardar_cambios():
            try:
                # Validar nombre
                nuevo_nombre = entry_nombre.get().strip()
                if not nuevo_nombre:
                    raise ValueError("¡Error! El nombre no puede estar vacío.")
                if len(nuevo_nombre) > 60:
                    raise ValueError("¡Error! El nombre es demasiado largo (máximo 60 letras).")

                # Función para validar lista de números con un máximo dinámico
                def validar_notas(texto, nombre_campo, max_notas):
                    partes = texto.split(",") if texto else []
                    numeros = []
                    for p in partes:
                        if not p.strip():
                            continue
                        try:
                            val = float(p)
                        except Exception:
                            raise ValueError(f"¡Error! '{p}' no es un número válido en {nombre_campo}.")

                        if not (0 <= val <= 100):
                            raise ValueError(f"¡Error! La nota {val} en {nombre_campo} debe estar entre 0 y 100.")
                        numeros.append(int(val))

                    if len(numeros) > max_notas:
                        raise ValueError(
                            f"¡Error! {nombre_campo} permite un máximo de {max_notas} nota(s) según la "
                            f"estructura calificativa actual. Tienes {len(numeros)}."
                        )
                    return numeros

                # Función para validar nota única
                def validar_unica(texto, nombre_campo):
                    if "," in texto:
                        raise ValueError(f"¡Error! Solo se permite una única nota para {nombre_campo}.")
                    try:
                        val = float(texto) if texto.strip() else 0
                    except Exception:
                        raise ValueError(f"¡Error! '{texto}' no es un número válido para {nombre_campo}.")

                    if not (0 <= val <= 100):
                        raise ValueError(f"¡Error! La nota de {nombre_campo} debe estar entre 0 y 100.")
                    return int(val)

                # Función para validar asistencia con el total de clases configurado
                def validar_asistencia(texto):
                    if "," in texto:
                        raise ValueError("¡Error! La asistencia es un único número de clases asistidas.")
                    try:
                        val = int(float(texto)) if texto.strip() else 0
                    except Exception:
                        raise ValueError(f"¡Error! '{texto}' no es un número válido para la asistencia.")

                    if not (0 <= val <= asis_total):
                        raise ValueError(
                            f"¡Error! El número de clases asistidas debe estar entre 0 y {asis_total} "
                            f"(total de clases del período)."
                        )
                    return val

                # Leer y validar límites desde config
                max_parciales    = limites.get("parciales",    3)
                max_labs         = limites.get("labs",         10)
                max_asignaciones = limites.get("asignaciones", 10)

                # Validar cada campo
                parciales_validados    = validar_notas(e_parciales.get(), "Parciales",    max_parciales)
                labs_validados         = validar_notas(e_labs.get(),      "Laboratorios", max_labs)
                asignaciones_validadas = validar_notas(e_asig.get(),      "Asignaciones", max_asignaciones)

                # Actualiza datos del estudiante
                est["nombre"] = nuevo_nombre
                est["notas"] = {
                    "final":        validar_unica(e_semestral.get(), "Semestral"),
                    "parciales":    parciales_validados,
                    "labs":         labs_validados,
                    "asignaciones": asignaciones_validadas,
                    "portafolio":   validar_unica(e_port.get(), "Portafolio"),
                    "asistencia":   validar_asistencia(e_asis.get())
                }

                # Guarda cambios en json local persistente y en la nube si hay red
                guardar()

                # Actualiza la interfaz visual de estudiantes
                actualizar_estudiantes()

                messagebox.showinfo("Éxito", "¡Notas actualizadas correctamente!")
                v.destroy()

            except ValueError as e:
                messagebox.showerror("Revisar Notas", str(e))
            except Exception as e:
                messagebox.showerror("Error inesperado", f"Ocurrió algo malo: {e}")

        # =========================
        # Botón para guardar o cerrar
        # =========================
        if rol != 'estudiante':
            tk.Button(
                v,
                text="Guardar Cambios",
                command=guardar_cambios,
                bg="lightgreen",
                height=2
            ).pack(pady=20)
        else:
            tk.Button(
                v,
                text="Cerrar",
                command=v.destroy,
                bg="lightblue",
                height=2
            ).pack(pady=20)