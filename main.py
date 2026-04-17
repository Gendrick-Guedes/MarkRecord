import os
import sys

# Forzar UTF-8 en la terminal de Windows para que los emojis no causen errores
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Asegurar que el directorio raíz del proyecto esté en el sys.path
root_path = os.path.dirname(os.path.abspath(__file__))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from launcher.selector import MainSelector
from auth.login import run_auth_flow

if __name__ == "__main__":
    try:
        # Asegurarnos de que estamos en el directorio correcto
        os.chdir(root_path)
        print(f"🚀 Iniciando Sistema Integrado...")
        print(f"📂 Directorio: {root_path}")
        
        # Iniciar sistema de Autorización en un bucle para soportar el "Cerrar sesión"
        while True:
            usuario_autenticado = run_auth_flow()
            
            # Una vez culminado, verifica si hay sesión (devolvió algo) o fue cerrado a la fuerza 
            if usuario_autenticado:
                print(f"✅ Autenticado como: {usuario_autenticado.get('role', 'estudiante')} ({usuario_autenticado.get('username', 'Unknown')})")
                MainSelector(current_user=usuario_autenticado)
            else:
                sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico al iniciar: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)