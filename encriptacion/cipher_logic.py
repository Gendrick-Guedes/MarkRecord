import os
from cryptography.fernet import Fernet

class FileCipher:
    def __init__(self):
        self.key = None

    def set_key(self, key_data):
        """Establece la llave actual para operaciones"""
        try:
            # Validar que sea una llave Fernet válida
            Fernet(key_data)
            self.key = key_data
            return True
        except:
            return False

    def generate_new_key(self):
        """Genera una nueva llave aleatoria"""
        return Fernet.generate_key()

    def encrypt_file(self, file_path, output_dir=None):
        if not self.key:
            raise Exception("No se ha cargado ninguna llave")
            
        f = Fernet(self.key)
        with open(file_path, "rb") as file:
            file_data = file.read()
        
        encrypted_data = f.encrypt(file_data)
        
        file_name = os.path.basename(file_path)
        # Añadimos .enc si no lo tiene
        if not file_name.endswith(".enc"):
            file_name += ".enc"
            
        if output_dir:
            output_path = os.path.join(output_dir, file_name)
        else:
            output_path = file_path + ".enc"
            
        with open(output_path, "wb") as file:
            file.write(encrypted_data)
        return output_path

    def decrypt_file(self, encrypted_file_path, output_dir=None):
        if not self.key:
            raise Exception("No se ha cargado ninguna llave")
            
        f = Fernet(self.key)
        with open(encrypted_file_path, "rb") as file:
            encrypted_data = file.read()
        
        try:
            decrypted_data = f.decrypt(encrypted_data)
            
            # Quitar la extensión .enc para el nombre de salida
            original_name = os.path.basename(encrypted_file_path)
            if original_name.endswith(".enc"):
                original_name = original_name[:-4]
            else:
                original_name = "decrypted_" + original_name

            if output_dir:
                output_path = os.path.join(output_dir, original_name)
            else:
                output_path = os.path.join(os.path.dirname(encrypted_file_path), original_name)
                
            with open(output_path, "wb") as file:
                file.write(decrypted_data)
            return output_path
        except Exception:
            raise Exception("¡Error! La llave es incorrecta o el archivo no es válido.")
