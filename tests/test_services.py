"""Tests para servicios."""
import unittest
from src.services.survey_service import SurveyService
from src.models.survey import SurveyResponse
from src.models.question import Question


class TestSurveyService(unittest.TestCase):
    """Tests para SurveyService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.service = SurveyService()
    
    def test_calculate_score(self):
        """Test cálculo de puntaje."""
        # Crear preguntas
        q1 = Question(id=1, text="P1", penalty_graduated=5.0, penalty_not_graduated=10.0)
        q2 = Question(id=2, text="P2", penalty_graduated=10.0, penalty_not_graduated=15.0)
        questions_map = {1: q1, 2: q2}
        
        # Respuestas: una NO, una YES
        responses = [
            SurveyResponse(id=1, survey_id=1, question_id=1, answer="NO", comment="Test", penalty_applied=0),
            SurveyResponse(id=2, survey_id=1, question_id=2, answer="YES", comment=None, penalty_applied=0)
        ]
        
        # Calcular puntaje (graduado)
        score = self.service.calculate_score(responses, True, questions_map)
        self.assertEqual(score, 95.0)  # 100 - 5
        
        # Calcular puntaje (no graduado)
        score = self.service.calculate_score(responses, False, questions_map)
        self.assertEqual(score, 90.0)  # 100 - 10
    
    def test_calculate_score_minimum_zero(self):
        """Test que el puntaje mínimo es 0."""
        q1 = Question(id=1, text="P1", penalty_graduated=150.0, penalty_not_graduated=150.0)
        questions_map = {1: q1}
        
        responses = [
            SurveyResponse(id=1, survey_id=1, question_id=1, answer="NO", comment="Test", penalty_applied=0)
        ]
        
        score = self.service.calculate_score(responses, True, questions_map)
        self.assertEqual(score, 0.0)  # No puede ser negativo


if __name__ == '__main__':
    unittest.main()

