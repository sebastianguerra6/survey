"""Repositorio para gestión de Tiers."""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.tier import Tier


class TierRepository(BaseRepository):
    """Repositorio para operaciones CRUD de tiers."""
    
    def create(self, tier: Tier) -> int:
        """Crea un nuevo tier y retorna su ID."""
        cursor = self.db.execute(
            """
            INSERT INTO tiers (area_id, name, min_score, max_score, description, color, active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tier.area_id,
                tier.name,
                tier.min_score,
                tier.max_score,
                tier.description,
                tier.color,
                1 if tier.active else 0
            )
        )
        tier_id = cursor.lastrowid
        self.log_audit('Tier', tier_id, 'CREATE', details=f"Tier {tier.name} ({tier.min_score}-{tier.max_score})")
        return tier_id
    
    def update(self, tier: Tier) -> bool:
        """Actualiza un tier existente."""
        if tier.id is None:
            raise ValueError("El tier debe tener ID para actualizarse")
        
        self.db.execute(
            """
            UPDATE tiers
            SET area_id = ?, name = ?, min_score = ?, max_score = ?, description = ?, color = ?, active = ?
            WHERE id = ?
            """,
            (
                tier.area_id,
                tier.name,
                tier.min_score,
                tier.max_score,
                tier.description,
                tier.color,
                1 if tier.active else 0,
                tier.id
            )
        )
        self.log_audit('Tier', tier.id, 'UPDATE', details=f"Tier {tier.name} ({tier.min_score}-{tier.max_score})")
        return True
    
    def delete(self, tier_id: int) -> bool:
        """Elimina (soft delete) un tier."""
        self.db.execute("UPDATE tiers SET active = 0 WHERE id = ?", (tier_id,))
        self.log_audit('Tier', tier_id, 'DELETE')
        return True
    
    def find_by_id(self, tier_id: int) -> Optional[Tier]:
        """Busca un tier por ID."""
        row = self.db.fetch_one(
            """
            SELECT id, area_id, name, min_score, max_score, description, color, active
            FROM tiers WHERE id = ?
            """,
            (tier_id,)
        )
        if row:
            return Tier(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                min_score=row['min_score'],
                max_score=row['max_score'],
                description=row['description'],
                color=row['color'],
                active=bool(row['active'])
            )
        return None
    
    def find_all(self, area_id: Optional[int] = None, active_only: bool = False) -> List[Tier]:
        """Obtiene todos los tiers, opcionalmente filtrados por área."""
        query = """
            SELECT id, area_id, name, min_score, max_score, description, color, active
            FROM tiers
        """
        conditions = []
        params: List = []
        
        if area_id is not None:
            conditions.append("area_id = ?")
            params.append(area_id)
        if active_only:
            conditions.append("active = 1")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY area_id, min_score DESC"
        
        rows = self.db.fetch_all(query, tuple(params))
        return [
            Tier(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                min_score=row['min_score'],
                max_score=row['max_score'],
                description=row['description'],
                color=row['color'],
                active=bool(row['active'])
            )
            for row in rows
        ]
    
    def find_by_score(self, area_id: int, score: float) -> Optional[Tier]:
        """Obtiene el tier que aplica para un puntaje en un área."""
        row = self.db.fetch_one(
            """
            SELECT id, area_id, name, min_score, max_score, description, color, active
            FROM tiers
            WHERE area_id = ? AND active = 1 AND ? BETWEEN min_score AND max_score
            ORDER BY min_score DESC
            LIMIT 1
            """,
            (area_id, score)
        )
        if row:
            return Tier(
                id=row['id'],
                area_id=row['area_id'],
                name=row['name'],
                min_score=row['min_score'],
                max_score=row['max_score'],
                description=row['description'],
                color=row['color'],
                active=bool(row['active'])
            )
        return None

