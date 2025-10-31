"""Modelo de Encuesta y Respuesta."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class SurveyResponse:
    """Representa una respuesta individual a una pregunta."""
    id: Optional[int]
    survey_id: int
    question_id: int
    answer: str  # 'Yes', 'No', 'N/A'
    penalty_applied: float = 0.0

    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if self.answer not in ['Yes', 'No', 'N/A']:
            raise ValueError("La respuesta debe ser 'Yes', 'No' o 'N/A'")


@dataclass
class Survey:
    """Representa una encuesta completa."""
    id: Optional[int]
    name: str
    sid: str
    case_id: int
    area_id: int
    position: str
    score: float
    created_at: datetime = field(default_factory=datetime.now)
    responses: List[SurveyResponse] = field(default_factory=list)

    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.name or not self.name.strip():
            raise ValueError("El nombre es obligatorio")
        if not self.sid or not self.sid.strip():
            raise ValueError("El SID es obligatorio")
        if self.case_id is None:
            raise ValueError("El caso es obligatorio")
        if self.area_id is None:
            raise ValueError("El área es obligatoria")
        if self.position not in ['Manager', 'Senior Manager', 'Analyst', 'Senior Analyst']:
            raise ValueError("Posición inválida")
        if self.score < 0:
            self.score = 0.0
        if self.score > 100:
            self.score = 100.0

