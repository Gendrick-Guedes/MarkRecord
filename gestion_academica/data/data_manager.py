import os
from gestion_academica.services.cloud_sync import CloudSync
from gestion_academica.models.notas import DEFAULT_CONFIG

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

def get_config():
    """
    Retorna la configuración actual del sistema de calificaciones.
    """
    return data.get("__config__", DEFAULT_CONFIG)

# =========================
# Guardar datos en Supabase (Modo Sincronización Total)
# =========================
def guardar():
    global data
    if "__config__" not in data:
        data["__config__"] = DEFAULT_CONFIG

    init_cloud()
    if cloud:
        print("🔥 Sincronización TOTAL con Supabase...")
        cloud.sync_all(data)
    else:
        print("❌ Error: No hay conexión con Supabase.")

# ===========================================================================
# MÉTODOS DE ACTUALIZACIÓN QUIRÚRGICA (Alta Velocidad)
# ===========================================================================

def guardar_estudiante_quirurgico(estudiante, asignatura, grupo):
    """
    Guarda o actualiza un único estudiante de forma quirúrgica.
    Si el estudiante no tiene ID, se crea y se le asigna el ID retornado.
    Si tiene ID, se actualiza el registro existente.
    """
    init_cloud()
    if not cloud:
        print("⚠️ Modo Offline: El cambio solo persistirá en memoria esta sesión.")
        return False
    
    try:
        if "id" in estudiante and estudiante["id"]:
            # ACTUALIZACIÓN (UPDATE)
            print(f"⚡ Editando estudiante '{estudiante['nombre']}' (ID: {estudiante['id']})")
            return cloud.actualizar_estudiante(estudiante)
        else:
            # CREACIÓN (INSERT)
            print(f"➕ Creando nuevo estudiante '{estudiante['nombre']}' en la nube...")
            nuevo_id = cloud.guardar_estudiante(asignatura, grupo, estudiante)
            if nuevo_id:
                estudiante["id"] = nuevo_id
                return True
    except Exception as e:
        print(f"❌ Error en guardado quirúrgico: {e}")
        return False
    return False

def eliminar_estudiante_quirurgico(estudiante):
    """Elimina un único estudiante de la nube de forma rápida."""
    init_cloud()
    if not cloud: return False
    
    try:
        est_id = estudiante.get("id")
        if est_id:
            print(f"🗑️ Eliminando estudiante por ID: {est_id}")
            return cloud.eliminar_estudiante_por_id(est_id)
        else:
            print(f"🗑️ Eliminando estudiante por nombre: {estudiante['nombre']}")
            return cloud.eliminar_estudiante(estudiante['nombre'])
    except Exception as e:
        print(f"❌ Error al eliminar de la nube: {e}")
        return False

# ===========================================================================
# Cargar datos desde Supabase
# ===========================================================================
def cargar():
    global data
    print("🌐 Cargando datos desde Supabase...")
    try:
        init_cloud()
        if cloud:
            db_data = cloud.get_all()
            if db_data:
                data.clear()
                data.update(db_data)
                if "__config__" not in data:
                    data["__config__"] = DEFAULT_CONFIG
                print("✅ Datos cargados exitosamente.")
                return
    except Exception as e:
        print(f"⚠️ Error al sincronizar: {e}")

    data.clear()
    data["__config__"] = DEFAULT_CONFIG
    print("🆕 Iniciando ambiente limpio.")