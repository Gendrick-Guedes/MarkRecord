from config.db import DatabaseAuth

def update_schema():
    db = DatabaseAuth()
    sql_commands = [
        "ALTER TABLE estudiantes ADD COLUMN IF NOT EXISTS parciales JSONB DEFAULT '[]'::jsonb;",
        "ALTER TABLE estudiantes ADD COLUMN IF NOT EXISTS labs JSONB DEFAULT '[]'::jsonb;",
        "ALTER TABLE estudiantes ADD COLUMN IF NOT EXISTS asignaciones JSONB DEFAULT '[]'::jsonb;",
        "ALTER TABLE estudiantes ADD COLUMN IF NOT EXISTS asistencia INTEGER DEFAULT 0;"
    ]
    
    for sql in sql_commands:
        print(f"Executing: {sql}")
        success = db.ejecutar_accion(sql)
        if success:
            print("  Success")
        else:
            print("  Failed")

if __name__ == "__main__":
    update_schema()
