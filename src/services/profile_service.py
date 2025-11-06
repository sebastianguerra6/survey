"""Servicio de lógica de negocio para Perfiles."""
from typing import List, Optional
from src.models.profile import Profile
from src.repositories.profile_repository import ProfileRepository


class ProfileService:
    """Servicio para lógica de negocio de perfiles."""
    
    def __init__(self):
        """Inicializa el servicio."""
        self.profile_repo = ProfileRepository()
    
    def create_profile(self, name: str, active: bool = True) -> int:
        """Crea un nuevo perfil."""
        profile = Profile(id=None, name=name, active=active)
        return self.profile_repo.create(profile)
    
    def update_profile(self, profile_id: int, name: str, active: bool) -> bool:
        """Actualiza un perfil existente."""
        profile = Profile(id=profile_id, name=name, active=active)
        return self.profile_repo.update(profile)
    
    def delete_profile(self, profile_id: int) -> bool:
        """Elimina un perfil."""
        return self.profile_repo.delete(profile_id)
    
    def get_profile(self, profile_id: int) -> Optional[Profile]:
        """Obtiene un perfil por ID."""
        return self.profile_repo.find_by_id(profile_id)
    
    def get_all_profiles(self, active_only: bool = True) -> List[Profile]:
        """Obtiene todos los perfiles."""
        return self.profile_repo.find_all(active_only=active_only)

