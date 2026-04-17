from tkinter import simpledialog, messagebox
import random
import string
from gestion_academica.ui.ui_listas import limpiar_nombre
from gestion_academica.data.data_manager import guardar_estudiante_quirurgico, eliminar_estudiante_quirurgico

# =======================
# Gestión de asignaturas
# =======================

# Función para agregar una nueva asignatura
def agregar_asignatura(data, guardar, actualizar):

    # Solicita nombre de la asignatura
    nombre = simpledialog.askstring("Asignatura", "Nombre de la asignatura:")

    # Verifica que se haya ingresado algo
    if nombre:
        # Límite de caracteres razonable
        if len(nombre) > 50:
            messagebox.showwarning("Límite", "El nombre de la asignatura no debe superar los 50 caracteres.")
            return

        # Evita duplicados
        if nombre not in data:

            # Crea nueva asignatura vacía
            data[nombre] = {}

            # Guarda cambios en json y mysql
            guardar()

            # Actualiza la interfaz
            actualizar()

        else:
            # Muestra error si ya existe
            messagebox.showwarning("Error", "La asignatura ya existe")


# Función para eliminar una o varias asignaturas
def eliminar_asignatura(data, guardar, lista_asignaturas, lista_grupos, lista_estudiantes, actualizar):

    # Obtenemos todos los elementos que tienen el checkbox marcado [x]
    nombres_a_borrar = []
    for i in range(lista_asignaturas.size()):
        item = lista_asignaturas.get(i)
        if item.startswith("[x]"):
            nombres_a_borrar.append(item[4:]) # Quitamos el "[x] "

    if nombres_a_borrar:
        # Confirmación del usuario
        mensaje = "¿Eliminar las asignaturas marcadas?" if len(nombres_a_borrar) > 1 else "¿Eliminar asignatura?"
        if messagebox.askyesno("Confirmar", mensaje):

            for nombre in nombres_a_borrar:
                if nombre in data:
                    del data[nombre]

            # Guarda cambios
            guardar()

            # Limpia las listas visuales
            lista_grupos.delete(0, "end")
            lista_estudiantes.delete(0, "end")
            
            # Actualiza la lista de asignaturas
            actualizar()


# ==================
# Gestión de grupos
# ==================

# Función para agregar un grupo a una asignatura
def agregar_grupo(data, guardar, lista_asignaturas, actualizar):

    # Obtiene asignatura seleccionada
    sel = lista_asignaturas.curselection()

    if not sel:
        return

    # Extraemos el nombre real usando limpiar_nombre
    a_display = lista_asignaturas.get(sel[0])
    a = limpiar_nombre(a_display)

    # Solicita nombre del grupo
    tipo = simpledialog.askstring("Grupo", "Nombre del grupo (Ej: Grupo A):")

    # Si el usuario ingresó algo
    if tipo:
        # Límite razonable
        if len(tipo) > 20:
            messagebox.showwarning("Límite", "El nombre del grupo no debe superar los 20 caracteres.")
            return

        # Verifica que la asignatura exista en data (por seguridad)
        if a in data:
            # Crea grupo vacío dentro de la asignatura
            data[a][tipo] = []

            # Guarda cambios
            guardar()

            # Actualiza la interfaz
            actualizar()
        else:
            messagebox.showerror("Error", f"No se encontró la asignatura: {a}")


# Función para eliminar uno o varios grupos
def eliminar_grupo(data, guardar, lista_asignaturas, lista_grupos, lista_estudiantes, actualizar):

    # Obtiene selección de asignatura
    sel_a = lista_asignaturas.curselection()
    
    # Obtenemos todos los grupos que tienen el checkbox marcado [x]
    nombres_g_a_borrar = []
    for i in range(lista_grupos.size()):
        item = lista_grupos.get(i)
        if item.startswith("[x]"):
            nombres_g_a_borrar.append(item[4:])

    if sel_a and nombres_g_a_borrar:

        # Confirmación del usuario
        mensaje = "¿Eliminar los grupos marcados?" if len(nombres_g_a_borrar) > 1 else "¿Eliminar grupo?"
        if messagebox.askyesno("Confirmar", mensaje):

            a_display = lista_asignaturas.get(sel_a[0])
            a = limpiar_nombre(a_display) # Quitamos prefijo si existe

            for g in nombres_g_a_borrar:
                if g in data[a]:
                    del data[a][g]

            # Guarda cambios
            guardar()

            # Limpia lista visual de estudiantes
            lista_estudiantes.delete(0, "end")
            
            # Actualiza la lista de grupos
            actualizar()


# =======================
# Gestión de estudiantes
# =======================

# Función para agregar un estudiante
def agregar_estudiante(data, guardar, lista_asignaturas, lista_grupos, actualizar):

    # Obtiene selección actual
    sel_a = lista_asignaturas.curselection()
    sel_g = lista_grupos.curselection()

    # Verifica que haya selección válida
    if not sel_a or not sel_g:
        return

    # Extraemos nombres reales usando limpiar_nombre
    a_display = lista_asignaturas.get(sel_a[0])
    g_display = lista_grupos.get(sel_g[0])
    
    a = limpiar_nombre(a_display)
    g = limpiar_nombre(g_display)

    # Solicita nombre del estudiante
    nombre = simpledialog.askstring("Estudiante", "Nombre completo:")

    if nombre:
        # Límite razonable
        if len(nombre) > 60:
            messagebox.showwarning("Límite", "El nombre del estudiante es demasiado largo (máx. 60).")
            return

        # Verifica que existan la asignatura y el grupo
        if a in data and g in data[a]:
            # Agrega estudiante con estructura inicial de notas estructurada para calculos futuros
            data[a][g].append({
            "nombre": nombre,
            "notas": {
                "final": 0,              # Semestral, inicialmente 0
                "parciales": [],         # Lista de parciales (30%)
                "labs": [],              # Lista de laboratorios (17%)
                "asignaciones": [],      # Lista de asignaciones (10%)
                "portafolio": 0,         # Nota del portafolio (5%)
                "asistencia": 0          # Clases asistidas en total (5%) - ahora se maneja como entero
            }
        })

        # Guarda cambios de forma quirúrgica (Alta velocidad)
        guardar_estudiante_quirurgico(data[a][g][-1], a, g)

        # Actualiza interfaz
        actualizar()

        # Mensaje de éxito
        messagebox.showinfo("Éxito", "Estudiante creado. Use 'Editar' para añadir sus notas.")


# Función para eliminar uno o varios estudiantes
def eliminar_estudiante(data, guardar, lista_asignaturas, lista_grupos, lista_estudiantes, actualizar):

    # Obtiene selecciones de asignatura y grupo
    sel_a = lista_asignaturas.curselection()
    sel_g = lista_grupos.curselection()
    
    # Obtenemos índices de estudiantes marcados con [x]
    indices_e = []
    for i in range(lista_estudiantes.size()):
        if lista_estudiantes.get(i).startswith("[x]"):
            indices_e.append(i)

    if sel_a and sel_g and indices_e:

        # Confirmación del usuario
        mensaje = "¿Eliminar los estudiantes marcados?" if len(indices_e) > 1 else "¿Eliminar estudiante?"
        if messagebox.askyesno("Confirmar", mensaje):

            a_display = lista_asignaturas.get(sel_a[0])
            g_display = lista_grupos.get(sel_g[0])
            
            a = limpiar_nombre(a_display)
            g = limpiar_nombre(g_display)

            # Eliminamos de atrás hacia adelante para no romper los índices
            for i in sorted(indices_e, reverse=True):
                if i < len(data[a][g]):
                    est = data[a][g].pop(i)
                    # Elimina de la nube de forma rápida
                    eliminar_estudiante_quirurgico(est)

            # Actualiza la interfaz de estudiantes
            actualizar()