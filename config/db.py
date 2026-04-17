import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Carga variables de entorno desde la carpeta config/ donde vive el .env
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_CONFIG_DIR, ".env"))

class DatabaseAuth:
    """Clase especializada para la conexión a la base de datos de Autenticación"""
    _instance = None

    def __new__(cls):
        # Patrón Singleton para mantener una sola conexión
        if cls._instance is None:
            cls._instance = super(DatabaseAuth, cls).__new__(cls)
            cls._instance.conn = None
            cls._instance.conectar()
        return cls._instance

    def conectar(self):
        try:
            self.conn = psycopg2.connect(
                os.getenv("DATABASE_URL"),
                connect_timeout=10
            )
            self.conn.autocommit = False
        except psycopg2.Error as e:
            print(f"❌ Error al conectar a la Base de Datos: {e}")
            self.conn = None

    def _ensure_connection(self):
        """Reconecta si la conexión está cerrada o perdida."""
        try:
            if self.conn is None or self.conn.closed:
                self.conectar()
            else:
                # Verifica que la conexión esté viva con un ping liviano
                with self.conn.cursor() as cur:
                    cur.execute("SELECT 1")
        except psycopg2.Error:
            self.conectar()

    def ejecutar_consulta(self, query, params=None):
        self._ensure_connection()
        if self.conn and not self.conn.closed:
            try:
                with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    cursor.execute(query, params or ())
                    return [dict(row) for row in cursor.fetchall()]
            except psycopg2.Error as e:
                print(f"❌ Error DB Consulta: {e}")
                self.conn.rollback()
                return []
        return []

    def ejecutar_accion(self, query, params=None):
        self._ensure_connection()
        if self.conn and not self.conn.closed:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                self.conn.commit()
                return True
            except psycopg2.Error as e:
                print(f"❌ Error DB Acción: {e}")
                self.conn.rollback()
                return False
        return False
