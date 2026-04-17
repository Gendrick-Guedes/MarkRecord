import os
import mysql.connector
from mysql.connector import Error
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
            self.conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                user=os.getenv("DB_USER", "root"),     
                password=os.getenv("DB_PASSWORD", "06102005"),
                database=os.getenv("DB_NAME", "gestion_academica"),
                port=os.getenv("DB_PORT", "3306")
            )
        except Error as e:
            print(f"❌ Error al conectar a la Base de Datos de Usuarios: {e}")
            self.conn = None

    def ejecutar_consulta(self, query, params=None):
        if self.conn and self.conn.is_connected():
            try:
                # To clear unread results, though dictionary=True usually reads all
                cursor = self.conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                res = cursor.fetchall()
                cursor.close()
                return res
            except Error as e:
                print(f"❌ Error DB Consulta: {e}")
                return []
        return []

    def ejecutar_accion(self, query, params=None):
        if self.conn and self.conn.is_connected():
            try:
                cursor = self.conn.cursor()
                cursor.execute(query, params or ())
                self.conn.commit()
                cursor.close()
                return True
            except Error as e:
                print(f"❌ Error DB Acción: {e}")
                self.conn.rollback()
                return False
        return False
