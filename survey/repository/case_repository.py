"""Repositorio para gestión de Casos."""
from typing import List, Optional
from ..database.db_connection import DatabaseConnection
from ..models.case import Case


class CaseRepository:
    """Repositorio para operaciones CRUD de Casos."""
    
    def __init__(self, db: DatabaseConnection = None):
        """Inicializa el repositorio."""
        self.db = db or DatabaseConnection()
    
    def create(self, case: Case) -> int:
        """Crea un nuevo caso y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO cases (name, active) VALUES (?, ?)",
            (case.name, 1 if case.active else 0)
        )
        return cursor.lastrowid
    
    def find_by_id(self, case_id: int) -> Optional[Case]:
        """Busca un caso por ID."""
        row = self.db.fetch_one(
            "SELECT id, name, active FROM cases WHERE id = ?",
            (case_id,)
        )
        if row:
            return Case(id=row['id'], name=row['name'], active=bool(row['active']))
        return None
    
    def find_all(self, active_only: bool = False) -> List[Case]:
        """Obtiene todos los casos."""
        query = "SELECT id, name, active FROM cases"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"
        
        rows = self.db.fetch_all(query)
        return [
            Case(id=row['id'], name=row['name'], active=bool(row['active']))
            for row in rows
        ]
    
    def update(self, case: Case) -> bool:
        """Actualiza un caso existente."""
        if case.id is None:
            raise ValueError("El caso debe tener un ID para ser actualizado")
        
        self.db.execute(
            "UPDATE cases SET name = ?, active = ? WHERE id = ?",
            (case.name, 1 if case.active else 0, case.id)
        )
        return True
    
    def delete(self, case_id: int) -> bool:
        """Elimina un caso (soft delete: marca como inactivo)."""
        self.db.execute(
            "UPDATE cases SET active = 0 WHERE id = ?",
            (case_id,)
        )
        return True
    
    def hard_delete(self, case_id: int) -> bool:
        """Elimina físicamente un caso de la base de datos."""
        self.db.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        return True

