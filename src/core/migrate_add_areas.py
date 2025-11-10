"""Script de migración para agregar tabla de áreas."""
from src.core.database import DatabaseConnection


def migrate_add_areas():
    """Agrega la tabla de áreas y modifica questions para incluir area_id."""
    db = DatabaseConnection()
    
    try:
        # Verificar si la tabla areas ya existe
        result = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='areas'"
        )
        
        if result is None:
            print("Creando tabla areas...")
            # Crear tabla areas
            db.execute_script("""
                CREATE TABLE IF NOT EXISTS areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHECK (active IN (0, 1))
                );
            """)
            print("Tabla areas creada.")
        else:
            print("Tabla areas ya existe.")
        
        # Verificar si questions tiene area_id
        result = db.fetch_one("PRAGMA table_info(questions)")
        columns = db.fetch_all("PRAGMA table_info(questions)")
        has_area_id = any(col['name'] == 'area_id' for col in columns)
        
        if not has_area_id:
            print("Agregando columna area_id a questions...")
            # Crear una área por defecto primero
            db.execute("INSERT INTO areas (name, description, active) VALUES (?, ?, ?)", 
                      ("General", "Área general por defecto", 1))
            default_area_id = db.fetch_one("SELECT id FROM areas WHERE name = 'General'")['id']
            
            # Agregar columna area_id a questions
            db.execute("ALTER TABLE questions ADD COLUMN area_id INTEGER")
            
            # Asignar área por defecto a todas las preguntas existentes
            db.execute("UPDATE questions SET area_id = ? WHERE area_id IS NULL", (default_area_id,))
            
            # Agregar foreign key constraint (SQLite no soporta ADD CONSTRAINT, pero podemos recrear la tabla)
            # Por ahora, solo actualizamos los datos existentes
            print("Columna area_id agregada y datos migrados.")
        else:
            print("Columna area_id ya existe en questions.")
        
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error en migración: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    migrate_add_areas()

