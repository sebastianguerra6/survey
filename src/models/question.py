"""Modelo de Pregunta."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    """Representa una pregunta del banco de preguntas."""
    id: Optional[int]
    text: str
    active: bool = True
    penalty_graduated: float = 0.0
    penalty_not_graduated: float = 0.0
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.text or not self.text.strip():
            raise ValueError("El texto de la pregunta no puede estar vacío")
        if self.penalty_graduated < 0:
            raise ValueError("La penalización para graduado no puede ser negativa")
        if self.penalty_not_graduated < 0:
            raise ValueError("La penalización para no graduado no puede ser negativa")
    
    def get_penalty(self, is_graduated: bool) -> float:
        """Retorna la penalización según si es graduado o no."""
        return self.penalty_graduated if is_graduated else self.penalty_not_graduated

