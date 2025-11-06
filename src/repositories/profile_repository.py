"""Repositorio para gestión de Perfiles."""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.profile import Profile


class ProfileRepository(BaseRepository):
    """Repositorio para operaciones CRUD de Perfiles."""
    
    def create(self, profile: Profile) -> int:
        """Crea un nuevo perfil y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO profiles (name, active) VALUES (?, ?)",
            (profile.name, 1 if profile.active else 0)
        )
        profile_id = cursor.lastrowid
        self.log_audit('Profile', profile_id, 'CREATE', details=f"Nombre: {profile.name}")
        return profile_id
    
    def find_by_id(self, profile_id: int) -> Optional[Profile]:
        """Busca un perfil por ID."""
        row = self.db.fetch_one("SELECT id, name, active FROM profiles WHERE id = ?", (profile_id,))
        if row:
            return Profile(id=row['id'], name=row['name'], active=bool(row['active']))
        return None
    
    def find_all(self, active_only: bool = False) -> List[Profile]:
        """Obtiene todos los perfiles."""
        query = "SELECT id, name, active FROM profiles"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY name"
        
        rows = self.db.fetch_all(query)
        return [Profile(id=row['id'], name=row['name'], active=bool(row['active'])) for row in rows]
    
    def update(self, profile: Profile) -> bool:
        """Actualiza un perfil existente."""
        if profile.id is None:
            raise ValueError("El perfil debe tener un ID para ser actualizado")
        
        self.db.execute(
            "UPDATE profiles SET name = ?, active = ? WHERE id = ?",
            (profile.name, 1 if profile.active else 0, profile.id)
        )
        self.log_audit('Profile', profile.id, 'UPDATE', details=f"Nombre: {profile.name}")
        return True
    
    def delete(self, profile_id: int) -> bool:
        """Elimina un perfil (soft delete)."""
        self.db.execute("UPDATE profiles SET active = 0 WHERE id = ?", (profile_id,))
        self.log_audit('Profile', profile_id, 'DELETE')
        return True

