import tkinter as tk
from tkinter import messagebox
from gestion_academica.ui.ui_listas import limpiar_nombre


# =========================
# Función principal de edición
# =========================
def editar(data, guardar, lista_asignaturas, lista_grupos, lista_estudiantes, actualizar_estudiantes, current_user=None):

    rol = current_user.get('role', 'estudiante').lower() if current_user else 'estudiante'
    
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
    # Editar estudiante
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
        v.title(f"Editando: {est['nombre']}")
        
        # Centrar asegurando que no se mueva a una esquina remota
        try:
            from launcher.selector import centrar_ventana
            centrar_ventana(v, 400, 550)
        except ImportError:
            v.geometry("400x550")

        # Hace que esta ventana secundaria sea modal (bloquea la interacción con
        # la ventana principal de gestión hasta que este formulario se cierre)
        v.grab_set()
        
        # Transient se asegura de que la sub-ventana minimice o restaure junto
        # a la ventana padre que la generó
        v.transient(v.master) 
        v.focus_set() # Pone el cursor/enfoque inmediatamente en esta ventanita

        # =========================
        # Función para crear campos de entrada con auto-puntuación
        # =========================
        def crear_campo(label, valor, es_lista=False, disabled=False):
            tk.Label(v, text=label, font=("Arial", 10, "bold")).pack()
            e = tk.Entry(v)
            e.insert(0, valor)
            
            if disabled:
                e.config(state="readonly")
                
            e.pack(pady=2)

            if es_lista and not disabled:
                # Evento para poner coma automática después de 2 dígitos
                def auto_coma(event):
                    # Solo si es un número y no estamos borrando
                    if event.keysym == "BackSpace": return
                    
                    content = e.get()
                    # Si los últimos 2 caracteres son números y no hay coma después
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
        bloquear_notas = (rol == 'estudiante')

        # Campo nombre
        entry_nombre = crear_campo("Nombre Estudiante", est["nombre"], disabled=bloquear_nombre)

        # Campo parciales (30%)
        e_parciales = crear_campo(
            "Parciales - 30%",
            ",".join(str(int(x)) for x in notas.get("parciales", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo labs (17%)
        e_labs = crear_campo(
            "Laboratorios - 17%",
            ",".join(str(int(x)) for x in notas.get("labs", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo asignaciones (10%)
        e_asig = crear_campo(
            "Asignaciones - 10%",
            ",".join(str(int(x)) for x in notas.get("asignaciones", [])),
            es_lista=True,
            disabled=bloquear_notas
        )

        # Campo portafolio (5%)
        e_port = crear_campo(
            "Portafolio - 5%",
            str(int(notas.get('portafolio', 0))),
            disabled=bloquear_notas
        )

        # Campo asistencia (5%)
        # Convertimos a entero por si viene como lista del formato anterior
        asis_val = notas.get("asistencia", 0)
        if isinstance(asis_val, list):
            asis_val = int(sum(asis_val)/len(asis_val)) if asis_val else 0
        
        e_asis = crear_campo(
            "Asistencia (Clases asistidas de 100) - 5%",
            str(int(asis_val)),
            disabled=bloquear_notas
        )

        # Campo semestral (33%)
        e_semestral = crear_campo(
            "Examen Semestral - 33%",
            str(int(notas.get('final', 0))),
            disabled=bloquear_notas
        )

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

                # Función para validar lista de números
                def validar_notas(texto, nombre_campo):
                    partes = texto.split(",") if texto else []
                    numeros = []
                    for p in partes:
                        if not p.strip(): continue
                        try:
                            val = float(p)
                        except:
                            raise ValueError(f"¡Error! '{p}' no es un número válido en {nombre_campo}.")
                        
                        if not (0 <= val <= 100):
                            raise ValueError(f"¡Error! La nota {val} en {nombre_campo} debe estar entre 0 y 100.")
                        numeros.append(int(val))
                    return numeros

                # Función para validar nota única
                def validar_unica(texto, nombre_campo):
                    if "," in texto:
                        raise ValueError(f"¡Error! Solo se permite una única nota para {nombre_campo}.")
                    try:
                        val = float(texto) if texto.strip() else 0
                    except:
                        raise ValueError(f"¡Error! '{texto}' no es un número válido para {nombre_campo}.")
                    
                    if not (0 <= val <= 100):
                        raise ValueError(f"¡Error! La nota de {nombre_campo} debe estar entre 0 y 100.")
                    return int(val)

                # Función para validar asistencia específica
                def validar_asistencia(texto):
                    if "," in texto:
                        raise ValueError("¡Error! La asistencia es un único número de clases (0-100).")
                    try:
                        val = int(float(texto)) if texto.strip() else 0
                    except:
                        raise ValueError(f"¡Error! '{texto}' no es un número válido para la asistencia.")
                    
                    if not (0 <= val <= 100):
                        raise ValueError(f"¡Error! El número de clases asistidas debe estar entre 0 y 100.")
                    return val

                # Actualiza datos
                parciales_validados = validar_notas(e_parciales.get(), "Parciales")
                if not (2 <= len(parciales_validados) <= 3):
                    raise ValueError("¡Error! En los parciales solo se permiten de 2 a 3 notas.")

                est["nombre"] = nuevo_nombre
                est["notas"] = {
                    "final": validar_unica(e_semestral.get(), "Semestral"),
                    "parciales": parciales_validados,
                    "labs": validar_notas(e_labs.get(), "Laboratorios"),
                    "asignaciones": validar_notas(e_asig.get(), "Asignaciones"),
                    "portafolio": validar_unica(e_port.get(), "Portafolio"),
                    "asistencia": validar_asistencia(e_asis.get())
                }

                # Guarda cambios en json local persistente y en mysql si hay red
                guardar()

                # Actualiza la interfaz visual de estudiantes de manera automática invocando 
                # a la función "actualizar_estudiantes" sin argumentos (porque desde main.py
                # ya viene recubierta en un lambda con los argumentos preparados)
                actualizar_estudiantes()

                messagebox.showinfo("Éxito", "¡Notas actualizadas correctamente!")
                v.destroy()

            except ValueError as e:
                messagebox.showerror("Revisar Notas", str(e))
            except Exception as e:
                messagebox.showerror("Error inesperado", f"Ocurrió algo malo: {e}")

        # =========================
        # Botón para guardar cambios
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