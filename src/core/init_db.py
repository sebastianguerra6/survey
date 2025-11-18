"""Inicialización de la base de datos."""
from pathlib import Path
from src.core.database import DatabaseConnection


def init_database():
    """Inicializa la base de datos con el esquema."""
    db = DatabaseConnection()
    
    # Leer schema
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Ejecutar schema
    db.execute_script(schema_sql)
    
    print("Base de datos inicializada correctamente.")


def check_database_tables():
    """Verifica si las tablas principales existen."""
    db = DatabaseConnection()
    try:
        result = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='profiles'"
        )
        return result is not None
    except Exception:
        return False


def ensure_database_initialized():
    """Asegura que la base de datos esté inicializada."""
    if not check_database_tables():
        print("Las tablas no existen, inicializando base de datos...")
        init_database()
    else:
        # Verificar si necesita migraciones
        db = DatabaseConnection()
        
        # Migración 1: tabla areas
        result = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='areas'"
        )
        if result is None:
            print("Aplicando migración para agregar tabla areas...")
            from src.core.migrate_add_areas import migrate_add_areas
            migrate_add_areas()
        
        # Migración 2: tabla cases y cambios en surveys
        result = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cases'"
        )
        if result is None:
            print("Aplicando migración para agregar tabla cases...")
            from src.core.migrate_add_cases import migrate_add_cases
            migrate_add_cases()
        
        # Verificar si surveys necesita actualización
        columns = db.fetch_all("PRAGMA table_info(surveys)")
        column_names = [col['name'] for col in columns]
        if 'sid' not in column_names or 'case_id' not in column_names:
            print("Aplicando migración para actualizar tabla surveys...")
            from src.core.migrate_add_cases import migrate_add_cases
            migrate_add_cases()
        
        # Migración 3: agregar area_id a cases
        if result is not None:  # Si la tabla cases existe
            columns = db.fetch_all("PRAGMA table_info(cases)")
            column_names = [col['name'] for col in columns]
            if 'area_id' not in column_names:
                print("Aplicando migración para agregar area_id a cases...")
                from src.core.migrate_add_area_to_cases import migrate_add_area_to_cases
                migrate_add_area_to_cases()
        
        # Migración 4: agregar sistema de tiers
        tiers_table = db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tiers'"
        )
        surveys_columns = db.fetch_all("PRAGMA table_info(surveys)")
        survey_column_names = [col['name'] for col in surveys_columns]
        needs_tiers_migration = (
            tiers_table is None
            or 'tier_id' not in survey_column_names
            or 'tier_name' not in survey_column_names
        )
        if needs_tiers_migration:
            print("Aplicando migración para agregar sistema de tiers...")
            from src.core.migrate_add_tiers import migrate_add_tiers
            migrate_add_tiers()
        
        print("Base de datos verificada.")


if __name__ == '__main__':
    init_database()

