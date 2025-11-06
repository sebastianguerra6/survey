"""Modelos de Encuesta."""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Survey:
    """Representa una encuesta de evaluación."""
    id: Optional[int]
    evaluator_profile: str
    analyst_name: str
    is_graduated: bool
    final_score: float = 0.0
    created_at: Optional[datetime] = None
    responses: List['SurveyResponse'] = None
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if not self.evaluator_profile or not self.evaluator_profile.strip():
            raise ValueError("El perfil del evaluador es obligatorio")
        if not self.analyst_name or not self.analyst_name.strip():
            raise ValueError("El nombre del analista es obligatorio")
        if self.final_score < 0 or self.final_score > 100:
            raise ValueError("El puntaje debe estar entre 0 y 100")
        if self.responses is None:
            self.responses = []


@dataclass
class SurveyResponse:
    """Representa una respuesta individual en una encuesta."""
    id: Optional[int]
    survey_id: int
    question_id: int
    answer: str  # 'YES', 'NO', 'NA'
    comment: Optional[str] = None
    penalty_applied: float = 0.0
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if self.answer not in ['YES', 'NO', 'NA']:
            raise ValueError("La respuesta debe ser 'YES', 'NO' o 'NA'")
        if self.answer == 'NO' and (not self.comment or not self.comment.strip()):
            raise ValueError("El comentario es obligatorio para respuestas 'NO'")
        if self.penalty_applied < 0:
            raise ValueError("La penalización no puede ser negativa")

