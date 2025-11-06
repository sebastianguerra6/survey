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
        print("Base de datos ya existe.")


if __name__ == '__main__':
    init_database()

