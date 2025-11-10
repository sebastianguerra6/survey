"""Repositorio para gestión de Casos."""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.case import Case


class CaseRepository(BaseRepository):
    """Repositorio para operaciones CRUD de Casos."""
    
    def create(self, case: Case) -> int:
        """Crea un nuevo caso y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO cases (area_id, name, description, active) VALUES (?, ?, ?, ?)",
            (case.area_id, case.name, case.description, 1 if case.active else 0)
        )
        case_id = cursor.lastrowid
        self.log_audit('Case', case_id, 'CREATE', details=f"Nombre: {case.name}, Área ID: {case.area_id}")
        return case_id
    
    def find_by_id(self, case_id: int) -> Optional[Case]:
        """Busca un caso por ID."""
        row = self.db.fetch_one(
            "SELECT id, area_id, name, description, active FROM cases WHERE id = ?",
            (case_id,)
        )
        if row:
            return Case(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                description=row['description'],
                active=bool(row['active'])
            )
        return None
    
    def find_by_name(self, name: str, area_id: Optional[int] = None) -> Optional[Case]:
        """Busca un caso por nombre, opcionalmente filtrado por área."""
        if area_id is not None:
            row = self.db.fetch_one(
                "SELECT id, area_id, name, description, active FROM cases WHERE name = ? AND area_id = ?",
                (name, area_id)
            )
        else:
            row = self.db.fetch_one(
                "SELECT id, area_id, name, description, active FROM cases WHERE name = ?",
                (name,)
            )
        if row:
            return Case(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                description=row['description'],
                active=bool(row['active'])
            )
        return None
    
    def find_all(self, active_only: bool = False, area_id: Optional[int] = None) -> List[Case]:
        """Obtiene todos los casos, opcionalmente filtrados por área."""
        query = "SELECT id, area_id, name, description, active FROM cases"
        conditions = []
        if active_only:
            conditions.append("active = 1")
        if area_id is not None:
            conditions.append("area_id = ?")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY name"
        
        params = (area_id,) if area_id is not None else ()
        rows = self.db.fetch_all(query, params)
        return [
            Case(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                description=row['description'],
                active=bool(row['active'])
            )
            for row in rows
        ]
    
    def update(self, case: Case) -> bool:
        """Actualiza un caso existente."""
        if case.id is None:
            raise ValueError("El caso debe tener un ID para ser actualizado")
        
        self.db.execute(
            "UPDATE cases SET area_id = ?, name = ?, description = ?, active = ? WHERE id = ?",
            (case.area_id, case.name, case.description, 1 if case.active else 0, case.id)
        )
        self.log_audit('Case', case.id, 'UPDATE', details=f"Nombre: {case.name}, Área ID: {case.area_id}")
        return True
    
    def delete(self, case_id: int) -> bool:
        """Elimina un caso (soft delete)."""
        self.db.execute("UPDATE cases SET active = 0 WHERE id = ?", (case_id,))
        self.log_audit('Case', case_id, 'DELETE')
        return True

