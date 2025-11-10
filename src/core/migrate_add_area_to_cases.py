"""Script de migración para agregar area_id a la tabla cases."""
from src.core.database import DatabaseConnection


def migrate_add_area_to_cases():
    """Agrega la columna area_id a la tabla cases y actualiza los datos existentes."""
    db = DatabaseConnection()
    
    try:
        # Verificar si la columna area_id ya existe
        columns = db.fetch_all("PRAGMA table_info(cases)")
        column_names = [col['name'] for col in columns]
        
        if 'area_id' not in column_names:
            print("Agregando columna area_id a la tabla cases...")
            
            # Obtener o crear un área por defecto
            default_area = db.fetch_one("SELECT id FROM areas WHERE name = 'General'")
            if not default_area:
                # Si no existe 'General', usar la primera área disponible
                default_area = db.fetch_one("SELECT id FROM areas LIMIT 1")
                if not default_area:
                    # Si no hay áreas, crear una por defecto
                    db.execute("INSERT INTO areas (name, description, active) VALUES (?, ?, ?)", 
                              ("General", "Área general por defecto", 1))
                    default_area = db.fetch_one("SELECT id FROM areas WHERE name = 'General'")
            
            default_area_id = default_area['id'] if default_area else None
            
            if default_area_id:
                # Agregar columna area_id
                db.execute("ALTER TABLE cases ADD COLUMN area_id INTEGER")
                
                # Actualizar casos existentes con el área por defecto
                db.execute("UPDATE cases SET area_id = ? WHERE area_id IS NULL", (default_area_id,))
                
                # Agregar foreign key constraint (SQLite no soporta ADD CONSTRAINT directamente)
                # Por ahora solo actualizamos los datos
                print("Columna area_id agregada y datos migrados.")
            else:
                print("Error: No se pudo obtener un área por defecto.")
        else:
            print("La columna area_id ya existe en la tabla cases.")
        
        # Verificar si necesita actualizar el UNIQUE constraint
        # SQLite no soporta modificar constraints directamente, así que solo verificamos
        print("Migración completada exitosamente.")
        
    except Exception as e:
        print(f"Error en migración: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    migrate_add_area_to_cases()

