import os
import json

from gestion_academica.services.cloud_sync import CloudSync

# Ruta al archivo de datos (ahora en gestion_academica/data/ junto a este módulo)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_JSON = os.path.join(BASE_DIR, "datos.json")

# =========================
# Almacenamiento en memoria
# =========================

# Diccionario global que guarda todos los datos del sistema
data = {}

# Conexión controlada para sincronización
cloud = None

def init_cloud():
    global cloud
    if cloud is None:
        try:
            cloud = CloudSync()
        except Exception as e:
            print(f"⚠️ Error al conectar con la nube: {e}")
            cloud = None

# =========================
# Guardar datos en json y MySQL
# =========================
def guardar():
    global data
    # Abre el archivo en modo escritura
    try:
        with open(DATOS_JSON, "w") as f:
            # Guarda el diccionario en formato json con indentación
            json.dump(data, f, indent=4)
        print(f"💾 Guardando JSON en: {DATOS_JSON}")
    except Exception as e:
        print(f"❌ Error al guardar JSON: {e}")
    
    # Sincroniza con MySQL
    init_cloud()
    if cloud:
        print("🔥 Sincronizando con MySQL...")
        cloud.sync_all(data)
    else:
        print("⏭️ Sincronización MySQL omitida (sin conexión)")


# ===========================================================================
# Cargar datos desde MySQL y JSON (Fusionados para prevenir pérdida de notas)
# ===========================================================================

def cargar():
    global data
    
    # 1. Cargamos el JSON local (Contiene todos los PARCIALES, LABS, ETC)
    json_data = {}
    try:
        with open(DATOS_JSON, "r") as f:
            json_data = json.load(f)
            print(f"📄 Datos locales leídos desde JSON: {DATOS_JSON}")
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print("⚠️ No hay JSON local o está corrupto.")

    # 2. Intentamos cargar y priorizar MySQL (Mantiene la estructura segura y Notas Finales)
    try:
        init_cloud()
        if cloud:
            db_data = cloud.get_all()
            
            # Si MySQL tiene datos, los unimos con el historial de JSON
            if db_data:
                # Recorremos la estructura recolectada de la DB
                for asig_nombre, grupos in db_data.items():
                    for grupo_nombre, estudiantes in grupos.items():
                        for est in estudiantes:
                            # Intentamos encontrar al mismo estudiante en el JSON local
                            try:
                                json_grupo = json_data.get(asig_nombre, {}).get(grupo_nombre, [])
                                json_est = next((e for e in json_grupo if e["nombre"] == est["nombre"]), None)
                                
                                # Si lo encontramos, le INYECTAMOS sus parciales para no perderlos,
                                # ya que MySQL local solo almacena "final" y "portafolio"
                                if json_est:
                                    est["notas"]["parciales"] = json_est["notas"].get("parciales", [])
                                    est["notas"]["labs"] = json_est["notas"].get("labs", [])
                                    est["notas"]["asignaciones"] = json_est["notas"].get("asignaciones", [])
                                    est["notas"]["asistencia"] = json_est["notas"].get("asistencia", 0)
                            except Exception as fail_merge:
                                pass # Si falla un estudiante, ignoramos y seguimos
                
                # Reemplaza todo el entorno local actual con los datos fusionados
                data.clear()
                data.update(db_data)
                print("🌐 Datos cargados desde MySQL (Fusionados exitosamente con historial JSON)")
                
                # IMPORTANTE: guardamos inmediatamente al iniciar para que el JSON se retroalimente
                guardar()
                return

    except Exception as e:
        print(f"⚠️ Error al sincronizar desde MySQL: {e}")

    # 3. Si MySQL falla por completo o está vacío, simplemente usamos el JSON recabado previamente
    data.clear()
    if json_data:
        data.update(json_data)
        print("⏭️ Trabajando únicamente con los datos de JSON (Modo Offline o DB Vacía)")
    else:
        print("🆕 Iniciando ambiente limpio y vacío.")