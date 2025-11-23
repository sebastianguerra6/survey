"""Comprobación de la base de datos SQL Server."""
from typing import List

from src.core.database import DatabaseConnection

REQUIRED_TABLES = [
    "profiles",
    "areas",
    "questions",
    "profile_question_defaults",
    "cases",
    "tiers",
    "surveys",
    "survey_responses",
    "audit_log",
]


def find_missing_tables() -> List[str]:
    """Devuelve la lista de tablas que no existen en SQL Server."""
    db = DatabaseConnection()
    missing = []
    for table in REQUIRED_TABLES:
        row = db.fetch_one(
            """
            SELECT 1 AS exists_flag
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME = ?
            """,
            (table,),
        )
        if row is None:
            missing.append(table)
    return missing


def ensure_database_initialized():
    """Valida que la base esté preparada; en caso contrario informa al usuario."""
    missing_tables = find_missing_tables()
    if missing_tables:
        missing_list = ", ".join(missing_tables)
        raise RuntimeError(
            "La base de datos SQL Server no tiene todas las tablas requeridas. "
            f"Faltan: {missing_list}. Ejecuta el script docs/sqlserver_schema.sql "
            "en tu instancia PCSEBASTIAN\\SQLEXPRESS01 y vuelve a intentarlo."
        )

