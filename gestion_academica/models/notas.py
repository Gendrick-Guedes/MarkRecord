# =========================
# Configuración por defecto del sistema de notas
# Esta se usa cuando no hay config guardada aún
# =========================
DEFAULT_CONFIG = {
    "pesos": {
        "final":       33,   # % Examen Semestral
        "parciales":   30,   # % Parciales
        "labs":        17,   # % Laboratorios
        "asignaciones":10,   # % Asignaciones/Tareas
        "portafolio":   5,   # % Portafolio
        "asistencia":   5    # % Asistencia
    },
    "limites": {
        "parciales":    3,   # Máximo de notas de parciales
        "labs":        10,   # Máximo de notas de laboratorios
        "asignaciones":10    # Máximo de notas de asignaciones
    },
    "asistencia_total": 30   # Total de clases en el período
}


# =========================
# Clase para cálculo de notas
# =========================
class SistemaNotas:

    # =========================
    # Inicialización
    # =========================
    def __init__(self, datos, config=None):
        # Guarda el diccionario de notas del estudiante
        self.datos = datos
        # Usa la configuración inyectada o la predeterminada
        self.config = config if config is not None else DEFAULT_CONFIG

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
        cfg = self.config

        # Extraer pesos desde la configuración (convertir de % a decimal)
        p = cfg.get("pesos", DEFAULT_CONFIG["pesos"])
        w_final       = p.get("final",        33) / 100
        w_parciales   = p.get("parciales",    30) / 100
        w_labs        = p.get("labs",         17) / 100
        w_asignaciones= p.get("asignaciones", 10) / 100
        w_portafolio  = p.get("portafolio",    5) / 100
        w_asistencia  = p.get("asistencia",    5) / 100

        # Total de clases configurado (para calcular % de asistencia)
        asistencia_total = cfg.get("asistencia_total", 30)

        # =========================
        # Obtener datos con valores por defecto
        # =========================
        final         = d.get("final", 0) or 0
        parciales     = d.get("parciales", [])
        labs          = d.get("labs", [])
        asignaciones  = d.get("asignaciones", [])
        portafolio    = d.get("portafolio", 0) or 0
        # Asistencia: número de clases asistidas
        asistencia_clases = d.get("asistencia", 0) or 0

        # Convertir clases asistidas a porcentaje (0-100)
        if asistencia_total > 0:
            asistencia_pct = min((asistencia_clases / asistencia_total) * 100, 100)
        else:
            asistencia_pct = 0

        # Inicializa nota final
        nota = 0

        # =========================
        # Cálculo por componentes con pesos dinámicos
        # =========================

        # Nota final / Semestral
        nota += final * w_final

        # Parciales
        if parciales:
            nota += (sum(parciales) / len(parciales)) * w_parciales

        # Laboratorios
        if labs:
            nota += (sum(labs) / len(labs)) * w_labs

        # Asignaciones
        if asignaciones:
            nota += (sum(asignaciones) / len(asignaciones)) * w_asignaciones

        # Portafolio
        nota += portafolio * w_portafolio

        # Asistencia (el % de asistencia real * el peso de asistencia)
        nota += asistencia_pct * w_asistencia

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