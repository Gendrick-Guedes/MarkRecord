import json
from config.db import DatabaseAuth

# =========================================
# Clase de sincronización con base de datos
# =========================================
class CloudSync:

    # Inicialización de conexión
    def __init__(self):
        self.db = DatabaseAuth()
        self._ensure_config_table()

    # =========================
    # Crear tabla de configuración si no existe
    # =========================
    def _ensure_config_table(self):
        """Crea la tabla 'configuracion' en la BD si no existe."""
        self.db.ejecutar_accion("""
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY DEFAULT 1,
                data TEXT NOT NULL
            )
        """)

    # =========================
    # Gestión de asignaturas
    # =========================

    # Guarda una asignatura en la base de datos
    def guardar_asignatura(self, nombre):
        self.db.ejecutar_accion(
            "INSERT INTO asignaturas (nombre) VALUES (%s)",
            (nombre,)
        )

    # Elimina una asignatura de la base de datos
    def eliminar_asignatura(self, nombre):
        self.db.ejecutar_accion(
            "DELETE FROM asignaturas WHERE nombre = %s",
            (nombre,)
        )

    # =========================
    # Gestión de grupos
    # =========================

    # Guarda un grupo asociado a una asignatura
    def guardar_grupo(self, asignatura, grupo):
        self.db.ejecutar_accion(
            "INSERT INTO grupos (nombre, asignatura) VALUES (%s, %s)",
            (grupo, asignatura)
        )

    # Elimina un grupo de la base de datos
    def eliminar_grupo(self, grupo):
        self.db.ejecutar_accion(
            "DELETE FROM grupos WHERE nombre = %s",
            (grupo,)
        )

    # =========================
    # Gestión de estudiantes
    # =========================

    # Guarda un estudiante con sus datos básicos
    def guardar_estudiante(self, asignatura, grupo, est):
        self.db.ejecutar_accion("""
            INSERT INTO estudiantes 
            (nombre, asignatura, grupo, final, portafolio)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            est["nombre"],
            asignatura,
            grupo,
            est["notas"]["final"],
            est["notas"]["portafolio"]
        ))

    # Elimina un estudiante por nombre
    def eliminar_estudiante(self, nombre):
        self.db.ejecutar_accion(
            "DELETE FROM estudiantes WHERE nombre = %s",
            (nombre,)
        )

    # Actualiza datos de un estudiante existente
    def actualizar_estudiante(self, est):
        self.db.ejecutar_accion("""
            UPDATE estudiantes 
            SET final=%s, portafolio=%s
            WHERE nombre=%s
        """, (
            est["notas"]["final"],
            est["notas"]["portafolio"],
            est["nombre"]
        ))

    # =========================
    # Guardar configuración calificativa
    # =========================
    def guardar_config(self, config):
        """Reemplaza la configuración guardada en la tabla 'configuracion'."""
        config_json = json.dumps(config)
        # Borrar la anterior e insertar la nueva (single-row config)
        self.db.ejecutar_accion("DELETE FROM configuracion")
        self.db.ejecutar_accion(
            "INSERT INTO configuracion (id, data) VALUES (1, %s)",
            (config_json,)
        )

    # =========================
    # Leer configuración calificativa
    # =========================
    def get_config(self):
        """Lee la configuración desde la BD. Retorna None si no hay."""
        rows = self.db.ejecutar_consulta("SELECT data FROM configuracion WHERE id = 1")
        if rows:
            try:
                return json.loads(rows[0]["data"])
            except Exception:
                return None
        return None

    # =========================
    # Sincronización completa (Carga desde JSON a MySQL)
    # =========================

    # Sincroniza todo el sistema local con la base de datos
    def sync_all(self, data):

        # Limpia la base de datos (reinicio total) para asegurar que se borre
        # cualquier dato viejo antes de insertar los nuevos en cascada
        self.db.ejecutar_accion("DELETE FROM estudiantes")
        self.db.ejecutar_accion("DELETE FROM grupos")
        self.db.ejecutar_accion("DELETE FROM asignaturas")

        # Recorre todas las asignaturas existentes en la memoria
        for asignatura, grupos in data.items():

            # Ignorar claves internas como __config__
            if asignatura.startswith("__"):
                continue

            self.guardar_asignatura(asignatura)

            # Recorre grupos de la asignatura actual
            for grupo, estudiantes in grupos.items():

                self.guardar_grupo(asignatura, grupo)

                # Recorre estudiantes del grupo actual
                for est in estudiantes:
                    self.guardar_estudiante(asignatura, grupo, est)

        # Sincronizar la configuración de calificaciones
        if "__config__" in data:
            self.guardar_config(data["__config__"])

    # =========================
    # Descarga de datos completa (DB -> Memoria Principal)
    # =========================
    def get_all(self):
        """
        Descarga todos la información base desde la BD y la organiza en
        el formato oficial de nuestro diccionario global (en memoria).
        La función data_manager.cargar() se encarga de llamar a este y luego
        combinar sus resultados con los parciales remanentes de datos.json
        """
        data = {}

        # 1. Obtener todas las asignaturas
        asignaturas = self.db.ejecutar_consulta("SELECT nombre FROM asignaturas")

        for asig in asignaturas:
            nombre_asig = asig['nombre']
            data[nombre_asig] = {}

            # 2. Obtener grupos para esta asignatura
            grupos = self.db.ejecutar_consulta("SELECT nombre FROM grupos WHERE asignatura = %s", (nombre_asig,))

            for grp in grupos:
                nombre_grp = grp['nombre']
                data[nombre_asig][nombre_grp] = []

                # 3. Obtener estudiantes para este grupo y asignatura
                estudiantes = self.db.ejecutar_consulta(
                    "SELECT nombre, final, portafolio FROM estudiantes WHERE asignatura = %s AND grupo = %s",
                    (nombre_asig, nombre_grp)
                )

                for est in estudiantes:
                    data[nombre_asig][nombre_grp].append({
                        "nombre": est['nombre'],
                        "notas": {
                            "final":        int(float(est['final'])),
                            "portafolio":   int(float(est['portafolio'])),
                            "parciales":    [],  # Estos se cargan del JSON si existen
                            "labs":         [],
                            "asignaciones": [],
                            "asistencia":   0
                        }
                    })

        # 4. Recuperar la configuración de calificaciones desde la BD
        config = self.get_config()
        if config:
            data["__config__"] = config

        return data