"""Pruebas para controladores."""
import pytest
import tempfile
import os
from survey.database.db_connection import DatabaseConnection
from survey.database.init_db import init_database
from survey.controllers.survey_controller import SurveyController
from survey.controllers.admin_controller import AdminController


@pytest.fixture
def temp_db():
    """Crea una base de datos temporal para pruebas."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_survey.db')
    
    original_get_db_path = DatabaseConnection._get_db_path
    
    def get_test_db_path():
        return db_path
    
    DatabaseConnection._get_db_path = staticmethod(get_test_db_path)
    DatabaseConnection._instance = None
    DatabaseConnection._connection = None
    
    init_database()
    
    yield db_path
    
    DatabaseConnection._get_db_path = staticmethod(original_get_db_path)
    db = DatabaseConnection()
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


class TestSurveyController:
    """Pruebas para SurveyController."""
    
    def test_calculate_score(self, temp_db):
        """Prueba cálculo de puntaje."""
        controller = SurveyController()
        
        # Crear área y pregunta de prueba
        admin_controller = AdminController()
        area_id = admin_controller.create_area("Área Test")
        
        question_id = admin_controller.create_question(
            area_id=area_id,
            text="¿Pregunta test?",
            position_weights={'Manager': 5.0}
        )
        
        question = admin_controller.get_question(question_id)
        
        # Test con respuesta "No" (debe penalizar)
        answers = {question_id: 'No'}
        score = controller.calculate_score([question], answers, 'Manager')
        assert score == 95.0  # 100 - 5
        
        # Test con respuesta "Yes" (no debe penalizar)
        answers = {question_id: 'Yes'}
        score = controller.calculate_score([question], answers, 'Manager')
        assert score == 100.0
        
        # Test con respuesta "N/A" (no debe penalizar)
        answers = {question_id: 'N/A'}
        score = controller.calculate_score([question], answers, 'Manager')
        assert score == 100.0


class TestAdminController:
    """Pruebas para AdminController."""
    
    def test_create_case(self, temp_db):
        """Prueba crear un caso."""
        controller = AdminController()
        case_id = controller.create_case("Caso Test")
        assert case_id > 0
        
        case = controller.get_case(case_id)
        assert case is not None
        assert case.name == "Caso Test"
    
    def test_create_area(self, temp_db):
        """Prueba crear un área."""
        controller = AdminController()
        area_id = controller.create_area("Área Test")
        assert area_id > 0
        
        area = controller.get_area(area_id)
        assert area is not None
        assert area.name == "Área Test"
    
    def test_create_question(self, temp_db):
        """Prueba crear una pregunta."""
        controller = AdminController()
        area_id = controller.create_area("Área Test")
        
        question_id = controller.create_question(
            area_id=area_id,
            text="¿Pregunta test?",
            position_weights={'Manager': 5.0}
        )
        assert question_id > 0
        
        question = controller.get_question(question_id)
        assert question is not None
        assert question.text == "¿Pregunta test?"

