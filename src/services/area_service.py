"""Servicio de lógica de negocio para Áreas."""
from typing import List, Optional
from src.models.area import Area
from src.repositories.area_repository import AreaRepository


class AreaService:
    """Servicio para lógica de negocio de áreas."""
    
    def __init__(self):
        """Inicializa el servicio."""
        self.area_repo = AreaRepository()
    
    def create_area(self, name: str, description: Optional[str] = None, active: bool = True) -> int:
        """Crea una nueva área."""
        area = Area(id=None, name=name, description=description, active=active)
        return self.area_repo.create(area)
    
    def update_area(self, area_id: int, name: str, description: Optional[str] = None, active: bool = True) -> bool:
        """Actualiza un área existente."""
        area = Area(id=area_id, name=name, description=description, active=active)
        return self.area_repo.update(area)
    
    def delete_area(self, area_id: int) -> bool:
        """Elimina un área."""
        return self.area_repo.delete(area_id)
    
    def get_area(self, area_id: int) -> Optional[Area]:
        """Obtiene un área por ID."""
        return self.area_repo.find_by_id(area_id)
    
    def get_all_areas(self, active_only: bool = True) -> List[Area]:
        """Obtiene todas las áreas."""
        return self.area_repo.find_all(active_only=active_only)

