"""Repositorio para gestión de Áreas."""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.area import Area


class AreaRepository(BaseRepository):
    """Repositorio para operaciones CRUD de Áreas."""
    
    def create(self, area: Area) -> int:
        """Crea una nueva área y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO areas (name, description, active) VALUES (?, ?, ?)",
            (area.name, area.description, 1 if area.active else 0)
        )
        area_id = cursor.lastrowid
        self.log_audit('Area', area_id, 'CREATE', details=f"Nombre: {area.name}")
        return area_id
    
    def find_by_id(self, area_id: int) -> Optional[Area]:
        """Busca un área por ID."""
        row = self.db.fetch_one(
            "SELECT id, name, description, active FROM areas WHERE id = ?",
            (area_id,)
        )
        if row:
            return Area(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                active=bool(row['active'])
            )
        return None
    
    def find_all(self, active_only: bool = False) -> List[Area]:
        """Obtiene todas las áreas."""
        query = "SELECT id, name, description, active FROM areas"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"
        
        rows = self.db.fetch_all(query)
        return [
            Area(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                active=bool(row['active'])
            )
            for row in rows
        ]
    
    def update(self, area: Area) -> bool:
        """Actualiza un área existente."""
        if area.id is None:
            raise ValueError("El área debe tener un ID para ser actualizada")
        
        self.db.execute(
            "UPDATE areas SET name = ?, description = ?, active = ? WHERE id = ?",
            (area.name, area.description, 1 if area.active else 0, area.id)
        )
        self.log_audit('Area', area.id, 'UPDATE', details=f"Nombre: {area.name}")
        return True
    
    def delete(self, area_id: int) -> bool:
        """Elimina un área (soft delete)."""
        self.db.execute("UPDATE areas SET active = 0 WHERE id = ?", (area_id,))
        self.log_audit('Area', area_id, 'DELETE')
        return True

