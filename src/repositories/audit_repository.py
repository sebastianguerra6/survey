"""Repositorio para gestión de Log de Auditoría."""
from typing import List, Optional
from datetime import datetime
from src.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository):
    """Repositorio para consultas del log de auditoría."""
    
    def get_all(self, limit: int = 100) -> List[dict]:
        """Obtiene todas las entradas del log de auditoría."""
        rows = self.db.fetch_all(
            """SELECT id, entity_type, entity_id, action, user_profile, details, created_at
               FROM audit_log ORDER BY created_at DESC LIMIT ?""",
            (limit,)
        )
        return [
            {
                'id': row['id'],
                'entity_type': row['entity_type'],
                'entity_id': row['entity_id'],
                'action': row['action'],
                'user_profile': row['user_profile'],
                'details': row['details'],
                'created_at': row['created_at']
            }
            for row in rows
        ]
    
    def get_by_entity(self, entity_type: str, entity_id: int) -> List[dict]:
        """Obtiene el log de auditoría para una entidad específica."""
        rows = self.db.fetch_all(
            """SELECT id, entity_type, entity_id, action, user_profile, details, created_at
               FROM audit_log WHERE entity_type = ? AND entity_id = ?
               ORDER BY created_at DESC""",
            (entity_type, entity_id)
        )
        return [
            {
                'id': row['id'],
                'entity_type': row['entity_type'],
                'entity_id': row['entity_id'],
                'action': row['action'],
                'user_profile': row['user_profile'],
                'details': row['details'],
                'created_at': row['created_at']
            }
            for row in rows
        ]

