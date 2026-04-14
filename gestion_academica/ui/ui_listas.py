import tkinter as tk
from gestion_academica.models.notas import SistemaNotas
import random

def limpiar_nombre(texto):
    if texto.startswith("[ ] ") or texto.startswith("[x] "):
        return texto[4:]
    return texto

#==========================
# Actualizar lista de asignaturas
#==========================

def actualizar_asignaturas(lista_asignaturas, data, mostrar_checkbox=True):
    # Limpia la lista visual
    lista_asignaturas.delete(0, tk.END)

    # Inserta todas las asignaturas ordenadas con o sin prefijo de checkbox
    for a in sorted(data.keys()):
        prefijo = "[ ] " if mostrar_checkbox else ""
        lista_asignaturas.insert(tk.END, f"{prefijo}{a}")

#==========================
# Actualizar lista de grupos
#==========================

def actualizar_grupos(lista_grupos, lista_asignaturas, data, mostrar_checkbox=True):
    # Limpia la lista visual
    lista_grupos.delete(0, tk.END)

    # Obtiene la asignatura seleccionada
    sel = lista_asignaturas.curselection()
    if not sel:
        return

    # Extraemos el nombre real (quitando el prefijo "[ ] " o "[x] ")
    a_display = lista_asignaturas.get(sel[0])
    a = limpiar_nombre(a_display)

    # Inserta los grupos de la asignatura seleccionada con o sin prefijo de checkbox
    if a in data:
        for g in sorted(data[a].keys()):
            prefijo = "[ ] " if mostrar_checkbox else ""
            lista_grupos.insert(tk.END, f"{prefijo}{g}")

#==========================
# Actualizar lista de estudiantes
#==========================
def actualizar_estudiantes(lista_estudiantes, lista_asignaturas, lista_grupos, data, mostrar_checkbox=True):
    # Limpia la lista visual
    lista_estudiantes.delete(0, tk.END)

    # Obtiene selección actual
    sel_a = lista_asignaturas.curselection()
    sel_g = lista_grupos.curselection()

    # Si no hay selección, no hace nada
    if not sel_a or not sel_g:
        return

    # Obtiene asignatura y grupo seleccionados (quitando prefijos)
    a_display = lista_asignaturas.get(sel_a[0])
    g_display = lista_grupos.get(sel_g[0])
    
    a = limpiar_nombre(a_display)
    g = limpiar_nombre(g_display)

    # Recorre todos los estudiantes del grupo
    if a in data and g in data[a]:
        for est in data[a][g]:

            if isinstance(est["notas"], list):
                est["notas"] = {
                    "final": random.uniform(70, 90),
                    "parciales": est["notas"],
                    "labs": [],
                    "asignaciones": [],
                    "portafolio": 80,
                    "asistencia": 100
                }

#=====================================
# Validar que todas las claves existan
#=====================================

            notas_dict = est["notas"]
            claves = ["final", "parciales", "labs", "asignaciones", "portafolio", "asistencia"]

            for c in claves:
                if c not in notas_dict:
                    # Si falta, asigna valor por defecto
                    notas_dict[c] = 0 if c in ["final", "portafolio", "asistencia"] else []

#============================
# Calcular nota final y letra
#============================

            calc = SistemaNotas(notas_dict)
            nota = calc.calcular()
            letra = calc.letra(nota)

            # Mostrar estudiante en la lista con o sin prefijo de checkbox
            prefijo = "[ ] " if mostrar_checkbox else ""
            lista_estudiantes.insert(
                tk.END,
                f"{prefijo}{est['nombre']} → {letra} ({nota:.1f})"
            )