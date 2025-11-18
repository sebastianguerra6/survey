"""Servicio de lógica para tiers."""
from typing import List, Optional, Iterable, Tuple
from src.models.tier import Tier
from src.repositories.tier_repository import TierRepository


class TierService:
    """Servicio para administración de tiers."""
    
    def __init__(self):
        self.tier_repo = TierRepository()
    
    def create_tier(self, area_id: int, name: str, min_score: float, max_score: float,
                    description: Optional[str] = None, color: Optional[str] = None,
                    active: bool = True) -> int:
        """Crea un nuevo tier."""
        tier = Tier(
            id=None,
            area_id=area_id,
            name=name,
            min_score=min_score,
            max_score=max_score,
            description=description,
            color=color,
            active=active
        )
        return self.tier_repo.create(tier)
    
    def update_tier(self, tier_id: int, area_id: int, name: str, min_score: float, max_score: float,
                    description: Optional[str] = None, color: Optional[str] = None,
                    active: bool = True) -> bool:
        """Actualiza un tier existente."""
        tier = Tier(
            id=tier_id,
            area_id=area_id,
            name=name,
            min_score=min_score,
            max_score=max_score,
            description=description,
            color=color,
            active=active
        )
        return self.tier_repo.update(tier)
    
    def delete_tier(self, tier_id: int) -> bool:
        """Desactiva un tier."""
        return self.tier_repo.delete(tier_id)
    
    def get_tier(self, tier_id: int) -> Optional[Tier]:
        """Obtiene un tier por ID."""
        return self.tier_repo.find_by_id(tier_id)
    
    def get_tiers(self, area_id: Optional[int] = None, active_only: bool = False) -> List[Tier]:
        """Obtiene tiers filtrados por área."""
        return self.tier_repo.find_all(area_id=area_id, active_only=active_only)
    
    def get_tier_for_score(self, area_id: int, score: float) -> Optional[Tier]:
        """Obtiene el tier correspondiente para un puntaje."""
        return self.tier_repo.find_by_score(area_id, score)
    
    def ensure_default_tiers(self, area_id: int, defaults: Iterable[Tuple[str, float, float, str, str]]):
        """Crea tiers por defecto si no existen para un área."""
        existing = self.get_tiers(area_id=area_id, active_only=False)
        existing_names = {tier.name for tier in existing}
        for name, min_score, max_score, description, color in defaults:
            if name in existing_names:
                continue
            try:
                self.create_tier(
                    area_id=area_id,
                    name=name,
                    min_score=min_score,
                    max_score=max_score,
                    description=description,
                    color=color,
                    active=True
                )
            except Exception:
                # Si hay algún error (por ejemplo, solapamiento), continuar
                continue

