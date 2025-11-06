"""Repositorio base con funcionalidad común."""
from typing import Optional
from src.core.database import DatabaseConnection


class BaseRepository:
    """Repositorio base con funcionalidad común."""
    
    def __init__(self, db: Optional[DatabaseConnection] = None):
        """Inicializa el repositorio."""
        self.db = db or DatabaseConnection()
    
    def log_audit(self, entity_type: str, entity_id: Optional[int], action: str, 
                  user_profile: Optional[str] = None, details: Optional[str] = None):
        """Registra una acción en el log de auditoría."""
        self.db.execute(
            """INSERT INTO audit_log (entity_type, entity_id, action, user_profile, details)
               VALUES (?, ?, ?, ?, ?)""",
            (entity_type, entity_id, action, user_profile, details)
        )

