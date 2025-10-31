"""Repositorio para gestión de Áreas."""
from typing import List, Optional
from ..database.db_connection import DatabaseConnection
from ..models.area import Area


class AreaRepository:
    """Repositorio para operaciones CRUD de Áreas."""
    
    def __init__(self, db: DatabaseConnection = None):
        """Inicializa el repositorio."""
        self.db = db or DatabaseConnection()
    
    def create(self, area: Area) -> int:
        """Crea una nueva área y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO areas (name, active) VALUES (?, ?)",
            (area.name, 1 if area.active else 0)
        )
        return cursor.lastrowid
    
    def find_by_id(self, area_id: int) -> Optional[Area]:
        """Busca un área por ID."""
        row = self.db.fetch_one(
            "SELECT id, name, active FROM areas WHERE id = ?",
            (area_id,)
        )
        if row:
            return Area(id=row['id'], name=row['name'], active=bool(row['active']))
        return None
    
    def find_by_name(self, name: str) -> Optional[Area]:
        """Busca un área por nombre."""
        row = self.db.fetch_one(
            "SELECT id, name, active FROM areas WHERE name = ?",
            (name,)
        )
        if row:
            return Area(id=row['id'], name=row['name'], active=bool(row['active']))
        return None
    
    def find_all(self, active_only: bool = False) -> List[Area]:
        """Obtiene todas las áreas."""
        query = "SELECT id, name, active FROM areas"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"
        
        rows = self.db.fetch_all(query)
        return [
            Area(id=row['id'], name=row['name'], active=bool(row['active']))
            for row in rows
        ]
    
    def update(self, area: Area) -> bool:
        """Actualiza un área existente."""
        if area.id is None:
            raise ValueError("El área debe tener un ID para ser actualizada")
        
        self.db.execute(
            "UPDATE areas SET name = ?, active = ? WHERE id = ?",
            (area.name, 1 if area.active else 0, area.id)
        )
        return True
    
    def delete(self, area_id: int) -> bool:
        """Elimina un área (soft delete: marca como inactivo)."""
        self.db.execute(
            "UPDATE areas SET active = 0 WHERE id = ?",
            (area_id,)
        )
        return True
    
    def hard_delete(self, area_id: int) -> bool:
        """Elimina físicamente un área de la base de datos."""
        self.db.execute("DELETE FROM areas WHERE id = ?", (area_id,))
        return True

