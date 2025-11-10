"""Script de migración para agregar tabla de casos y cambiar analyst_name por sid."""
from src.core.database import DatabaseConnection


def migrate_add_cases():
    """Agrega la tabla de casos y modifica surveys para usar sid y case_id."""
    db = DatabaseConnection()
    
    try:
        # Verificar si la tabla cases ya existe
        result = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cases'"
        )
        
        if result is None:
            print("Creando tabla cases...")
            # Crear tabla cases
            db.execute_script("""
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHECK (active IN (0, 1))
                );
            """)
            print("Tabla cases creada.")
        else:
            print("Tabla cases ya existe.")
        
        # Verificar si surveys tiene sid y case_id
        columns = db.fetch_all("PRAGMA table_info(surveys)")
        column_names = [col['name'] for col in columns]
        has_sid = 'sid' in column_names
        has_case_id = 'case_id' in column_names
        has_analyst_name = 'analyst_name' in column_names
        
        if not has_sid or not has_case_id:
            print("Modificando tabla surveys...")
            
            # Crear un caso por defecto si no existe
            default_case = db.fetch_one("SELECT id FROM cases WHERE name = 'Caso General'")
            if not default_case:
                db.execute("INSERT INTO cases (name, description, active) VALUES (?, ?, ?)", 
                          ("Caso General", "Caso general por defecto", 1))
                default_case_id = db.fetch_one("SELECT id FROM cases WHERE name = 'Caso General'")['id']
            else:
                default_case_id = default_case['id']
            
            # Agregar columnas si no existen
            if not has_sid:
                db.execute("ALTER TABLE surveys ADD COLUMN sid TEXT")
                # Migrar datos: si existe analyst_name, copiarlo a sid
                if has_analyst_name:
                    db.execute("UPDATE surveys SET sid = analyst_name WHERE sid IS NULL")
                else:
                    db.execute("UPDATE surveys SET sid = 'N/A' WHERE sid IS NULL")
                print("Columna sid agregada.")
            
            if not has_case_id:
                db.execute("ALTER TABLE surveys ADD COLUMN case_id INTEGER")
                db.execute("UPDATE surveys SET case_id = ? WHERE case_id IS NULL", (default_case_id,))
                print("Columna case_id agregada y datos migrados.")
            
            # Eliminar columna analyst_name si existe (SQLite no soporta DROP COLUMN directamente)
            # Por ahora la dejamos, pero no se usará
            print("Tabla surveys actualizada.")
        else:
            print("Tabla surveys ya tiene sid y case_id.")
        
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error en migración: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    migrate_add_cases()

