import json
import os
import sys

# Añadir el path del proyecto para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

from gestion_academica.services.cloud_sync import CloudSync

def migrate_final():
    json_path = os.path.join(project_root, "gestion_academica", "data", "datos.json")
    if not os.path.exists(json_path):
        print(f"Error: No se encontro datos.json en {json_path}")
        return

    print(f"Iniciando migracion final desde {json_path} a Supabase...")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        cloud = CloudSync()
        print("Sincronizando datos masivos (Optimizado)...")
        cloud.sync_all(data)
        print("Migracion completada con exito.")
        
        # Opcional: renombrar el json para que no se use más
        new_path = json_path + ".backup"
        if os.path.exists(new_path):
            os.remove(new_path)
        os.rename(json_path, new_path)
        print(f"El archivo original ha sido renombrado a {new_path}")
        
    except Exception as e:
        print(f"Error durante la migracion: {e}")

if __name__ == "__main__":
    migrate_final()
