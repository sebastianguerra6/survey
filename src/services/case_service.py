"""Servicio de lógica de negocio para Casos."""
from typing import List, Optional
from src.models.case import Case
from src.repositories.case_repository import CaseRepository


class CaseService:
    """Servicio para lógica de negocio de casos."""
    
    def __init__(self):
        """Inicializa el servicio."""
        self.case_repo = CaseRepository()
    
    def create_case(self, area_id: int, name: str, description: Optional[str] = None, active: bool = True) -> int:
        """Crea un nuevo caso."""
        case = Case(id=None, area_id=area_id, name=name, description=description, active=active)
        return self.case_repo.create(case)
    
    def find_or_create_case(self, area_id: int, name: str) -> int:
        """Busca un caso por nombre y área, si no existe lo crea."""
        case = self.case_repo.find_by_name(name, area_id=area_id)
        if case:
            return case.id
        else:
            return self.create_case(area_id=area_id, name=name, active=True)
    
    def update_case(self, case_id: int, area_id: int, name: str, description: Optional[str] = None, active: bool = True) -> bool:
        """Actualiza un caso existente."""
        case = Case(id=case_id, area_id=area_id, name=name, description=description, active=active)
        return self.case_repo.update(case)
    
    def delete_case(self, case_id: int) -> bool:
        """Elimina un caso."""
        return self.case_repo.delete(case_id)
    
    def get_case(self, case_id: int) -> Optional[Case]:
        """Obtiene un caso por ID."""
        return self.case_repo.find_by_id(case_id)
    
    def get_all_cases(self, active_only: bool = True, area_id: Optional[int] = None) -> List[Case]:
        """Obtiene todos los casos, opcionalmente filtrados por área."""
        return self.case_repo.find_all(active_only=active_only, area_id=area_id)

