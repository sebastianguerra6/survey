"""Modelo de Perfil."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Profile:
    """Representa un perfil de evaluador."""
    id: Optional[int]
    name: str
    active: bool = True
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del perfil no puede estar vacío")

