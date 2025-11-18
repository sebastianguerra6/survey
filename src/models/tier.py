"""Modelo de Tier."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tier:
    """Representa un rango de evaluación para un área."""
    id: Optional[int]
    area_id: int
    name: str
    min_score: float
    max_score: float
    description: Optional[str] = None
    color: Optional[str] = None
    active: bool = True
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if self.area_id is None:
            raise ValueError("El área es obligatoria")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del tier es obligatorio")
        if self.min_score < 0 or self.max_score > 100:
            raise ValueError("Los puntajes deben estar entre 0 y 100")
        if self.min_score > self.max_score:
            raise ValueError("El puntaje mínimo no puede ser mayor al máximo")

