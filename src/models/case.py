"""Modelo de Caso."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Case:
    """Representa un caso de evaluación."""
    id: Optional[int]
    area_id: int
    name: str
    description: Optional[str] = None
    active: bool = True
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if self.area_id is None:
            raise ValueError("El área es obligatoria")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del caso no puede estar vacío")

