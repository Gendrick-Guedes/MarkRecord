import tkinter as tk
from tkinter import messagebox
import random
import string

# =========================
# Generador automático de datos
# =========================
def generar_datos(data, guardar, actualizar_asignaturas):

    # =========================
    # Creación de ventana emergente
    # =========================
    v = tk.Toplevel()
    v.title("Generador Automático")
    
    # Importar función de centrado
    try:
        from launcher.selector import centrar_ventana
        centrar_ventana(v, 350, 300)
    except ImportError:
        v.geometry("350x300")

    # Hace la ventana modal y siempre al frente
    v.grab_set()
    v.transient(v.master)
    v.focus_set()

    # Variables para opciones del usuario
    var_grupos = tk.BooleanVar(value=True)
    var_estudiantes = tk.BooleanVar(value=True)

    # =========================
    # Interfaz de opciones
    # =========================
    tk.Label(v, text="Opciones de generación", font=("Arial", 12, "bold")).pack(pady=10)

    # Checkbox para decidir si crear grupos
    tk.Checkbutton(v, text="Crear grupos", variable=var_grupos).pack()

    # Checkbox para decidir si crear estudiantes
    tk.Checkbutton(v, text="Crear estudiantes", variable=var_estudiantes).pack()

    # Campo para cantidad de asignaturas
    tk.Label(v, text="Cantidad de asignaturas:").pack(pady=5)
    cantidad_entry = tk.Entry(v)
    cantidad_entry.insert(0, "1")
    cantidad_entry.pack()

    # =========================
    # Función que ejecuta la generación
    # =========================
    def ejecutar():

        # Función para generar prefijos tipo A, B, C... Z, Aa, Ab... Az, Ba, Bb...
        def obtener_prefijo(n):
            if n < 26:
                return chr(65 + n) # A, B... Z
            
            # Para n >= 26, usamos lógica tipo Excel
            # Primera letra (Mayúscula): A, B, C...
            # Segunda letra (Minúscula): a, b, c...
            idx_first = (n // 26) - 1
            idx_last = n % 26
            
            return obtener_prefijo(idx_first) + chr(97 + idx_last)

        # Lista de posibles nombres de materias
        materias_nombres = [
            "Programación", "Matemáticas", "Física", "Base de Datos", "IA", 
            "Cálculo", "Redes", "Sistemas Operativos", "Ética Profesional", 
            "Inglés Técnico", "Diseño Web", "Estructura de Datos", 
            "Álgebra Lineal", "Arquitectura de Software", "Ciberseguridad",
            "Gestión de Proyectos", "Inteligencia de Negocios", "Robótica",
            "Desarrollo Móvil", "Minería de Datos", "Simulación", "Auditoría"
        ]

        # Lista de nombres de estudiantes
        nombres_est = [
            "Ana", "Juan", "Pedro", "Maria", "Luis", "Elena", "Pablo", "Lucia", 
            "Carlos", "Sofia", "Diego", "Paula", "Andrés", "Beatriz", "Camilo", 
            "Daniela", "Esteban", "Fernanda", "Gabriel", "Helena", "Ignacio", 
            "Julia", "Kevin", "Laura", "Mateo", "Natalia", "Oscar", "Patricia", 
            "Ricardo", "Sara", "Tomás", "Valeria", "William", "Ximena", "Yolanda"
        ]

        try:
            # Convierte la cantidad ingresada a número
            cantidad = int(cantidad_entry.get())
            
            # Limitar a máximo 20 asignaturas para evitar colapsos
            if cantidad > 20:
                messagebox.showwarning("Límite excedido", "Por seguridad, solo puedes generar hasta 20 asignaturas a la vez.")
                return
            
            if cantidad <= 0:
                messagebox.showwarning("Error", "La cantidad debe ser mayor a 0.")
                return

            # =========================
            # Generación de asignaturas
            # =========================
            # Buscamos cuántas asignaturas ya existen para seguir el orden de letras
            prefijo_idx = len(data) 

            for _ in range(cantidad):

                # Escoge una materia base
                materia_base = random.choice(materias_nombres)
                
                # Busca el siguiente número disponible para esta materia base (Matemáticas 1, Matemáticas 2...)
                # Analizamos los nombres de las materias actuales en 'data'
                conteo = 1
                while True:
                    materia = f"{materia_base} {conteo}"
                    if materia not in data:
                        break
                    conteo += 1

                # Si no existe, la crea
                data[materia] = {}

                # =========================
                # Generación de grupos (1 a 10 grupos con el mismo prefijo de letra)
                # =========================
                if var_grupos.get():
                    num_grupos = random.randint(1, 10)
                    letra_prefijo = obtener_prefijo(prefijo_idx)
                    
                    for i in range(num_grupos):
                        # Todos los grupos de esta materia comparten la misma letra, pero cambia el número
                        # Ejemplo: A0, A1, A2... o B0, B1...
                        nombre_grupo = f"{letra_prefijo}{i}"
                        data[materia][nombre_grupo] = []

                        # =========================
                        # Generación de estudiantes
                        # =========================
                        if var_estudiantes.get():
                            for _ in range(random.randint(5, 12)):

                                # Genera nombre aleatorio tipo "Ana A."
                                nombre = f"{random.choice(nombres_est)} {random.choice(string.ascii_uppercase)}."

                                # =========================
                                # Creación de estructura de notas (Solo números enteros)
                                # =========================
                                data[materia][nombre_grupo].append({
                                    "nombre": nombre,
                                    "notas": {
                                        "final": random.randint(50, 100),
                                        "parciales": [random.randint(40, 100) for _ in range(3)],
                                        "labs": [random.randint(60, 100) for _ in range(3)],
                                        "asignaciones": [random.randint(60, 100) for _ in range(2)],
                                        "portafolio": random.randint(50, 100),
                                        "asistencia": random.randint(80, 100)
                                    }
                                })
                
                # Siguiente asignatura tendrá la siguiente letra (B, C, D...)
                prefijo_idx += 1

            # =========================
            # Guardado y actualización
            # =========================
            guardar()  # Guarda en json y mysql
            actualizar_asignaturas()  # Refresca la interfaz

            # Mensaje de éxito
            messagebox.showinfo("OK", "Datos generados correctamente")

            # Cierra la ventana
            v.destroy()

        except:
            # Manejo de error si el input no es válido
            messagebox.showerror("Error", "Entrada inválida")

    # =========================
    # Botón para ejecutar generación
    # =========================
    tk.Button(
        v,
        text="Generar",
        command=ejecutar,
        bg="lightgreen"
    ).pack(pady=15)