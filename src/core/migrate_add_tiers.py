"""Migración para agregar tablas y columnas relacionadas con tiers."""
from src.core.database import DatabaseConnection


def migrate_add_tiers():
    """Crea la tabla tiers y agrega columnas tier_id/tier_name en surveys."""
    db = DatabaseConnection()
    
    # Crear tabla de tiers si no existe
    db.execute("""
        CREATE TABLE IF NOT EXISTS tiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            min_score REAL NOT NULL,
            max_score REAL NOT NULL,
            description TEXT,
            color TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE,
            UNIQUE(area_id, name),
            CHECK (min_score >= 0 AND max_score <= 100 AND min_score <= max_score),
            CHECK (active IN (0, 1))
        )
    """)
    
    # Asegurar índices
    db.execute("CREATE INDEX IF NOT EXISTS idx_tiers_area ON tiers(area_id)")
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_tiers_area_score "
        "ON tiers(area_id, min_score, max_score)"
    )
    
    # Agregar columnas a surveys si no existen
    columns = db.fetch_all("PRAGMA table_info(surveys)")
    column_names = [col['name'] for col in columns]
    
    if 'tier_id' not in column_names:
        db.execute("ALTER TABLE surveys ADD COLUMN tier_id INTEGER")
    
    if 'tier_name' not in column_names:
        db.execute("ALTER TABLE surveys ADD COLUMN tier_name TEXT")


if __name__ == '__main__':
    migrate_add_tiers()

