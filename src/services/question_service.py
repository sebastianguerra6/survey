"""Servicio de lógica de negocio para Preguntas."""
from typing import List, Optional
from src.models.question import Question
from src.repositories.question_repository import QuestionRepository


class QuestionService:
    """Servicio para lógica de negocio de preguntas."""
    
    def __init__(self):
        """Inicializa el servicio."""
        self.question_repo = QuestionRepository()
    
    def create_question(self, area_id: int, text: str, penalty_graduated: float = 0.0, 
                       penalty_not_graduated: float = 0.0, active: bool = True) -> int:
        """Crea una nueva pregunta."""
        question = Question(
            id=None,
            area_id=area_id,
            text=text,
            active=active,
            penalty_graduated=penalty_graduated,
            penalty_not_graduated=penalty_not_graduated
        )
        return self.question_repo.create(question)
    
    def update_question(self, question_id: int, area_id: int, text: str, penalty_graduated: float,
                      penalty_not_graduated: float, active: bool) -> bool:
        """Actualiza una pregunta existente."""
        question = Question(
            id=question_id,
            area_id=area_id,
            text=text,
            active=active,
            penalty_graduated=penalty_graduated,
            penalty_not_graduated=penalty_not_graduated
        )
        return self.question_repo.update(question)
    
    def delete_question(self, question_id: int) -> bool:
        """Elimina una pregunta."""
        return self.question_repo.delete(question_id)
    
    def get_question(self, question_id: int) -> Optional[Question]:
        """Obtiene una pregunta por ID."""
        return self.question_repo.find_by_id(question_id)
    
    def get_all_questions(self, active_only: bool = False, area_id: Optional[int] = None) -> List[Question]:
        """Obtiene todas las preguntas, opcionalmente filtradas por área."""
        return self.question_repo.find_all(active_only=active_only, area_id=area_id)
    
    def set_default_answer(self, profile_id: int, question_id: int, default_answer: str) -> bool:
        """Establece la respuesta por defecto para un perfil y pregunta."""
        if default_answer not in ['YES', 'NO', 'NA']:
            raise ValueError("La respuesta por defecto debe ser 'YES', 'NO' o 'NA'")
        return self.question_repo.set_default_answer(profile_id, question_id, default_answer)
    
    def get_defaults_for_profile(self, profile_id: int) -> dict:
        """Obtiene todas las respuestas por defecto para un perfil."""
        return self.question_repo.get_defaults_for_profile(profile_id)

