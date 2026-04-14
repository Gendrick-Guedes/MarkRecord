# =========================
# Clase para cálculo de notas
# =========================
class SistemaNotas:

    # =========================
    # Inicialización
    # =========================
    def __init__(self, datos):
        # Guarda el diccionario de notas del estudiante
        self.datos = datos

    # =========================
    # Cálculo de promedio simple
    # =========================
    def promedio(self, lista):
        # Si la lista está vacía, retorna 0
        if not lista:
            return 0

        # Retorna promedio
        return sum(lista) / len(lista)

    # =========================
    # Cálculo de nota final
    # =========================
    def calcular(self):
        d = self.datos

        # =========================
        # Obtener datos con valores por defecto
        # =========================
        final = d.get("final", 0) or 0
        parciales = d.get("parciales", [])
        labs = d.get("labs", [])
        asignaciones = d.get("asignaciones", [])
        portafolio = d.get("portafolio", 0) or 0
        asistencia = d.get("asistencia", 0) or 0 # Ahora es un valor único (0-100)

        # Inicializa nota final
        nota = 0

        # =========================
        # Cálculo por componentes
        # =========================

        # Nota final (33%)
        nota += final * 0.33

        # Parciales (30%)
        if parciales:
            nota += (sum(parciales) / len(parciales)) * 0.30

        # Laboratorios (17%)
        if labs:
            nota += (sum(labs) / len(labs)) * 0.17

        # Asignaciones (10%)
        if asignaciones:
            nota += (sum(asignaciones) / len(asignaciones)) * 0.10

        # Portafolio (5%)
        nota += portafolio * 0.05

        # Asistencia (5%) - El valor representa el % de asistencia (ej: 80 = 80%)
        nota += asistencia * 0.05

        # =========================
        # Redondeo final
        # =========================
        return round(nota, 2)

    # =========================
    # Conversión a letra
    # =========================
    def letra(self, nota):

        # Asigna letra según rango de nota
        if nota >= 91:
            return "A"
        elif nota >= 81:
            return "B"
        elif nota >= 71:
            return "C"
        elif nota >= 61:
            return "D"
        else:
            return "F"