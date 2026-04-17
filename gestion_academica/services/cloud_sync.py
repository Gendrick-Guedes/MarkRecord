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

    def guardar_asignatura(self, nombre):
        self.db.ejecutar_accion(
            "INSERT INTO asignaturas (nombre) VALUES (%s)",
            (nombre,)
        )

    def eliminar_asignatura(self, nombre):
        self.db.ejecutar_accion(
            "DELETE FROM asignaturas WHERE nombre = %s",
            (nombre,)
        )

    # =========================
    # Gestión de grupos
    # =========================

    def guardar_grupo(self, asignatura, grupo):
        self.db.ejecutar_accion(
            "INSERT INTO grupos (nombre, asignatura) VALUES (%s, %s)",
            (grupo, asignatura)
        )

    def eliminar_grupo(self, grupo):
        self.db.ejecutar_accion(
            "DELETE FROM grupos WHERE nombre = %s",
            (grupo,)
        )

    # =========================
    # Gestión de estudiantes (QUIRÚRGICA)
    # =========================

    def guardar_estudiante(self, asignatura, grupo, est):
        """Guarda un estudiante y retorna su ID generado."""
        n = est["notas"]
        query = """
            INSERT INTO estudiantes 
            (nombre, asignatura, grupo, final, portafolio, parciales, labs, asignaciones, asistencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            est["nombre"],
            asignatura,
            grupo,
            n.get("final", 0),
            n.get("portafolio", 0),
            json.dumps(n.get("parciales", [])),
            json.dumps(n.get("labs", [])),
            json.dumps(n.get("asignaciones", [])),
            n.get("asistencia", 0)
        )
        
        # Como ejecutar_accion no retorna RETURNING, usamos ejecutar_consulta para obtener el ID
        res = self.db.ejecutar_consulta(query, params)
        return res[0]['id'] if res else None

    def eliminar_estudiante(self, nombre):
        self.db.ejecutar_accion(
            "DELETE FROM estudiantes WHERE nombre = %s",
            (nombre,)
        )

    def eliminar_estudiante_por_id(self, est_id):
        """Eliminación precisa por ID."""
        return self.db.ejecutar_accion("DELETE FROM estudiantes WHERE id = %s", (est_id,))

    def actualizar_estudiante(self, est):
        """Actualización quirúrgica usando ID."""
        est_id = est.get("id")
        if not est_id:
            # Fallback a nombre si no hay ID (no recomendado)
            print("⚠️ Advertencia: Actualizando por nombre (ID no encontrado)")
            return self.actualizar_estudiante_por_nombre(est)

        n = est["notas"]
        return self.db.ejecutar_accion("""
            UPDATE estudiantes 
            SET nombre=%s, final=%s, portafolio=%s, parciales=%s, labs=%s, asignaciones=%s, asistencia=%s
            WHERE id=%s
        """, (
            est["nombre"],
            n.get("final", 0),
            n.get("portafolio", 0),
            json.dumps(n.get("parciales", [])),
            json.dumps(n.get("labs", [])),
            json.dumps(n.get("asignaciones", [])),
            n.get("asistencia", 0),
            est_id
        ))

    def actualizar_estudiante_por_nombre(self, est):
        """Método legado por seguridad."""
        n = est["notas"]
        return self.db.ejecutar_accion("""
            UPDATE estudiantes 
            SET final=%s, portafolio=%s, parciales=%s, labs=%s, asignaciones=%s, asistencia=%s
            WHERE nombre=%s
        """, (
            n.get("final", 0),
            n.get("portafolio", 0),
            json.dumps(n.get("parciales", [])),
            json.dumps(n.get("labs", [])),
            json.dumps(n.get("asignaciones", [])),
            n.get("asistencia", 0),
            est["nombre"]
        ))

    # =========================
    # Gestión de configuración
    # =========================

    def guardar_config(self, config):
        config_json = json.dumps(config)
        self.db.ejecutar_accion("DELETE FROM configuracion")
        self.db.ejecutar_accion(
            "INSERT INTO configuracion (id, data) VALUES (1, %s)",
            (config_json,)
        )

    def get_config(self):
        rows = self.db.ejecutar_consulta("SELECT data FROM configuracion WHERE id = 1")
        if rows:
            try: return json.loads(rows[0]["data"])
            except: return None
        return None

    # ====================================================================
    # Sincronización completa (Uso masivo para carga inicial o backups)
    # ====================================================================
    def sync_all(self, data):
        self.db.ejecutar_accion("DELETE FROM estudiantes")
        self.db.ejecutar_accion("DELETE FROM grupos")
        self.db.ejecutar_accion("DELETE FROM asignaturas")

        asig_values = []
        grupos_values = []
        est_values = []

        for asignatura, grupos in data.items():
            if asignatura.startswith("__"): continue
            asig_values.append((asignatura,))
            for grupo, estudiantes in grupos.items():
                grupos_values.append((grupo, asignatura))
                for est in estudiantes:
                    n = est["notas"]
                    est_values.append((
                        est["nombre"], asignatura, grupo, n.get("final", 0), n.get("portafolio", 0),
                        json.dumps(n.get("parciales", [])),
                        json.dumps(n.get("labs", [])),
                        json.dumps(n.get("asignaciones", [])),
                        n.get("asistencia", 0)
                    ))

        if asig_values: self.db.ejecutar_lote("INSERT INTO asignaturas (nombre) VALUES %s", asig_values)
        if grupos_values: self.db.ejecutar_lote("INSERT INTO grupos (nombre, asignatura) VALUES %s", grupos_values)
        if est_values: self.db.ejecutar_lote("INSERT INTO estudiantes (nombre, asignatura, grupo, final, portafolio, parciales, labs, asignaciones, asistencia) VALUES %s", est_values)

        if "__config__" in data:
            self.guardar_config(data["__config__"])

    # ====================================================================
    # Descarga completa (Optimizado con inclusión de ID)
    # ====================================================================
    def get_all(self):
        new_data = {}

        asigs = self.db.ejecutar_consulta("SELECT nombre FROM asignaturas ORDER BY id")
        for a in asigs: new_data[a['nombre']] = {}

        grupos = self.db.ejecutar_consulta("SELECT nombre, asignatura FROM grupos")
        for g in grupos:
            if g['asignatura'] in new_data:
                new_data[g['asignatura']][g['nombre']] = []

        estudiantes = self.db.ejecutar_consulta("SELECT * FROM estudiantes")
        for e in estudiantes:
            asig, grp = e['asignatura'], e['grupo']
            if asig in new_data and grp in new_data[asig]:
                def decode_json(val):
                    if isinstance(val, str): return json.loads(val)
                    return val if val is not None else []

                new_data[asig][grp].append({
                    "id": e['id'],  # CLAVE PARA OPTIMIZACIÓN QUIRÚRGICA
                    "nombre": e['nombre'],
                    "notas": {
                        "final":        int(float(e['final'] or 0)),
                        "portafolio":   int(float(e['portafolio'] or 0)),
                        "parciales":    decode_json(e['parciales']),
                        "labs":         decode_json(e['labs']),
                        "asignaciones": decode_json(e['asignaciones']),
                        "asistencia":   e['asistencia'] or 0
                    }
                })

        config = self.get_config()
        if config: new_data["__config__"] = config
        return new_data