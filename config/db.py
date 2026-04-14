import os
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
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
            # Primero intenta usar DATABASE_URL (Supabase) directamente
            database_url = os.getenv("DATABASE_URL")
            
            if database_url:
                self.conn = psycopg2.connect(database_url)
            else:
                self.conn = psycopg2.connect(
                    host=os.getenv("DB_HOST", "127.0.0.1"),
                    user=os.getenv("DB_USER", "postgres"),     
                    password=os.getenv("DB_PASSWORD", ""),
                    dbname=os.getenv("DB_NAME", "postgres"),
                    port=os.getenv("DB_PORT", "5432")
                )
        except Error as e:
            print(f"❌ Error al conectar a la Base de Datos de Usuarios: {e}")
            self.conn = None

    def ejecutar_consulta(self, query, params=None):
        if self.conn and not self.conn.closed:
            try:
                cursor = self.conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute(query, params or ())
                return cursor.fetchall()
            except Error as e:
                print(f"❌ Error DB Consulta: {e}")
                self.conn.rollback() # Important in postgres on error
                return []
        return []

    def ejecutar_accion(self, query, params=None):
        if self.conn and not self.conn.closed:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                self.conn.commit()
                return True
            except Error as e:
                print(f"❌ Error DB Acción: {e}")
                self.conn.rollback()
                return False
        return False
