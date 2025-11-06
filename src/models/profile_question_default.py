"""Modelo de Respuesta por Defecto por Perfil."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileQuestionDefault:
    """Representa una respuesta por defecto para una pregunta según perfil."""
    id: Optional[int]
    profile_id: int
    question_id: int
    default_answer: str  # 'YES', 'NO', 'NA'
    
    def __post_init__(self):
        """Validaciones después de la inicialización."""
        if self.default_answer not in ['YES', 'NO', 'NA']:
            raise ValueError("La respuesta por defecto debe ser 'YES', 'NO' o 'NA'")

