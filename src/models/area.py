"""Modelo de Área."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Area:
    """Representa un área de evaluación."""
    id: Optional[int]
    name: str
    description: Optional[str] = None
    active: bool = True
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del área no puede estar vacío")

