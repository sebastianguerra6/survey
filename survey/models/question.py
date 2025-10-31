"""Modelo de Pregunta."""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Question:
    """Representa una pregunta en el sistema."""
    id: Optional[int]
    area_id: int
    text: str
    active: bool = True
    # Penalizaciones por posición: {position_name: penalty_value}
    position_weights: Dict[str, float] = None

    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.text or not self.text.strip():
            raise ValueError("El texto de la pregunta no puede estar vacío")
        if self.area_id is None:
            raise ValueError("El área es obligatoria")
        if self.position_weights is None:
            # Por defecto, vacío - significa que no aplica a ninguna posición
            self.position_weights = {}

    def get_penalty_for_position(self, position: str) -> float:
        """Obtiene la penalización para una posición específica.
        
        Si la posición no está en position_weights, retorna 0.0.
        Esto indica que la pregunta no aplica para esa posición.
        """
        return self.position_weights.get(position, 0.0)

