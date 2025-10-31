"""Modelo de Caso."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Case:
    """Representa un caso en el sistema."""
    id: Optional[int]
    name: str
    active: bool = True

    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del caso no puede estar vacío")

