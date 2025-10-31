"""Pruebas para modelos."""
import pytest
from survey.models.case import Case
from survey.models.area import Area
from survey.models.question import Question
from survey.models.survey import Survey, SurveyResponse
from datetime import datetime


class TestCase:
    """Pruebas para el modelo Case."""
    
    def test_create_case(self):
        """Prueba crear un caso válido."""
        case = Case(id=1, name="Caso Test", active=True)
        assert case.id == 1
        assert case.name == "Caso Test"
        assert case.active is True
    
    def test_case_empty_name_raises_error(self):
        """Prueba que un caso con nombre vacío lanza error."""
        with pytest.raises(ValueError):
            Case(id=1, name="", active=True)
        
        with pytest.raises(ValueError):
            Case(id=1, name="   ", active=True)


class TestArea:
    """Pruebas para el modelo Area."""
    
    def test_create_area(self):
        """Prueba crear un área válida."""
        area = Area(id=1, name="Área Test", active=True)
        assert area.id == 1
        assert area.name == "Área Test"
        assert area.active is True
    
    def test_area_empty_name_raises_error(self):
        """Prueba que un área con nombre vacío lanza error."""
        with pytest.raises(ValueError):
            Area(id=1, name="", active=True)


class TestQuestion:
    """Pruebas para el modelo Question."""
    
    def test_create_question(self):
        """Prueba crear una pregunta válida."""
        question = Question(
            id=1,
            area_id=1,
            text="¿Pregunta test?",
            active=True,
            position_weights={
                'Manager': 5.0,
                'Senior Manager': 10.0,
                'Analyst': 3.0,
                'Senior Analyst': 7.0
            }
        )
        assert question.id == 1
        assert question.area_id == 1
        assert question.text == "¿Pregunta test?"
        assert question.active is True
    
    def test_get_penalty_for_position(self):
        """Prueba obtener penalización por posición."""
        question = Question(
            id=1,
            area_id=1,
            text="Test",
            position_weights={'Manager': 5.0}
        )
        assert question.get_penalty_for_position('Manager') == 5.0
        assert question.get_penalty_for_position('Analyst') == 0.0


class TestSurvey:
    """Pruebas para el modelo Survey."""
    
    def test_create_survey(self):
        """Prueba crear una encuesta válida."""
        survey = Survey(
            id=1,
            name="Juan Pérez",
            sid="SID123",
            case_id=1,
            area_id=1,
            position="Manager",
            score=85.0
        )
        assert survey.id == 1
        assert survey.name == "Juan Pérez"
        assert survey.score == 85.0
        assert len(survey.responses) == 0
    
    def test_survey_score_clamping(self):
        """Prueba que el puntaje se ajusta a rango 0-100."""
        survey = Survey(
            id=1,
            name="Test",
            sid="SID",
            case_id=1,
            area_id=1,
            position="Manager",
            score=-10.0
        )
        assert survey.score == 0.0
        
        survey = Survey(
            id=1,
            name="Test",
            sid="SID",
            case_id=1,
            area_id=1,
            position="Manager",
            score=150.0
        )
        assert survey.score == 100.0
    
    def test_survey_response(self):
        """Prueba crear una respuesta de encuesta."""
        response = SurveyResponse(
            id=1,
            survey_id=1,
            question_id=1,
            answer="No",
            penalty_applied=5.0
        )
        assert response.answer == "No"
        assert response.penalty_applied == 5.0
    
    def test_survey_response_invalid_answer(self):
        """Prueba que respuesta inválida lanza error."""
        with pytest.raises(ValueError):
            SurveyResponse(
                id=1,
                survey_id=1,
                question_id=1,
                answer="Maybe",
                penalty_applied=0.0
            )

