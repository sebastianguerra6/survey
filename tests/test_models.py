"""Tests para modelos de datos."""
import unittest
from src.models.question import Question
from src.models.profile import Profile
from src.models.survey import Survey, SurveyResponse


class TestQuestion(unittest.TestCase):
    """Tests para el modelo Question."""
    
    def test_create_question(self):
        """Test creación de pregunta válida."""
        question = Question(
            id=1,
            text="¿Pregunta de prueba?",
            active=True,
            penalty_graduated=5.0,
            penalty_not_graduated=10.0
        )
        self.assertEqual(question.text, "¿Pregunta de prueba?")
        self.assertEqual(question.penalty_graduated, 5.0)
        self.assertEqual(question.penalty_not_graduated, 10.0)
    
    def test_get_penalty(self):
        """Test cálculo de penalización."""
        question = Question(
            id=1,
            text="Test",
            penalty_graduated=5.0,
            penalty_not_graduated=10.0
        )
        self.assertEqual(question.get_penalty(True), 5.0)
        self.assertEqual(question.get_penalty(False), 10.0)
    
    def test_invalid_penalty(self):
        """Test que penalización negativa lanza error."""
        with self.assertRaises(ValueError):
            Question(id=1, text="Test", penalty_graduated=-1.0)


class TestSurvey(unittest.TestCase):
    """Tests para el modelo Survey."""
    
    def test_create_survey(self):
        """Test creación de encuesta válida."""
        survey = Survey(
            id=1,
            evaluator_profile="Manager",
            analyst_name="Juan Pérez",
            is_graduated=True,
            final_score=85.0
        )
        self.assertEqual(survey.evaluator_profile, "Manager")
        self.assertEqual(survey.analyst_name, "Juan Pérez")
        self.assertEqual(survey.final_score, 85.0)
    
    def test_survey_response_no_comment(self):
        """Test que respuesta NO sin comentario lanza error."""
        with self.assertRaises(ValueError):
            SurveyResponse(
                id=1,
                survey_id=1,
                question_id=1,
                answer="NO",
                comment=None
            )


if __name__ == '__main__':
    unittest.main()

