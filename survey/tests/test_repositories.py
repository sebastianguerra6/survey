"""Pruebas para repositorios."""
import pytest
import os
import tempfile
from survey.database.db_connection import DatabaseConnection
from survey.database.init_db import init_database
from survey.repository.case_repository import CaseRepository
from survey.repository.area_repository import AreaRepository
from survey.repository.question_repository import QuestionRepository
from survey.models.case import Case
from survey.models.area import Area
from survey.models.question import Question


@pytest.fixture
def temp_db():
    """Crea una base de datos temporal para pruebas."""
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_survey.db')
    
    # Modificar DatabaseConnection para usar BD temporal
    original_get_db_path = DatabaseConnection._get_db_path
    
    def get_test_db_path():
        return db_path
    
    DatabaseConnection._get_db_path = staticmethod(get_test_db_path)
    DatabaseConnection._instance = None
    DatabaseConnection._connection = None
    
    # Inicializar BD
    init_database()
    
    yield db_path
    
    # Limpiar
    DatabaseConnection._get_db_path = staticmethod(original_get_db_path)
    db = DatabaseConnection()
    db.close()
    if os.path.exists(db_path):
        os.remove(db_path)


class TestCaseRepository:
    """Pruebas para CaseRepository."""
    
    def test_create_case(self, temp_db):
        """Prueba crear un caso."""
        repo = CaseRepository()
        case = Case(id=None, name="Caso Test", active=True)
        case_id = repo.create(case)
        assert case_id > 0
    
    def test_find_case_by_id(self, temp_db):
        """Prueba buscar caso por ID."""
        repo = CaseRepository()
        case = Case(id=None, name="Caso Test", active=True)
        case_id = repo.create(case)
        
        found = repo.find_by_id(case_id)
        assert found is not None
        assert found.name == "Caso Test"
    
    def test_find_all_cases(self, temp_db):
        """Prueba obtener todos los casos."""
        repo = CaseRepository()
        repo.create(Case(id=None, name="Caso 1", active=True))
        repo.create(Case(id=None, name="Caso 2", active=True))
        
        cases = repo.find_all()
        assert len(cases) >= 2


class TestAreaRepository:
    """Pruebas para AreaRepository."""
    
    def test_create_area(self, temp_db):
        """Prueba crear un área."""
        repo = AreaRepository()
        area = Area(id=None, name="Área Test", active=True)
        area_id = repo.create(area)
        assert area_id > 0
    
    def test_find_area_by_id(self, temp_db):
        """Prueba buscar área por ID."""
        repo = AreaRepository()
        area = Area(id=None, name="Área Test", active=True)
        area_id = repo.create(area)
        
        found = repo.find_by_id(area_id)
        assert found is not None
        assert found.name == "Área Test"


class TestQuestionRepository:
    """Pruebas para QuestionRepository."""
    
    def test_create_question(self, temp_db):
        """Prueba crear una pregunta."""
        # Crear área primero
        area_repo = AreaRepository()
        area_id = area_repo.create(Area(id=None, name="Área Test", active=True))
        
        question_repo = QuestionRepository()
        question = Question(
            id=None,
            area_id=area_id,
            text="¿Pregunta test?",
            active=True,
            position_weights={
                'Manager': 5.0,
                'Senior Manager': 10.0,
                'Analyst': 3.0,
                'Senior Analyst': 7.0
            }
        )
        question_id = question_repo.create(question)
        assert question_id > 0
    
    def test_find_question_by_area_and_position(self, temp_db):
        """Prueba buscar preguntas por área y posición."""
        # Crear área
        area_repo = AreaRepository()
        area_id = area_repo.create(Area(id=None, name="Área Test", active=True))
        
        question_repo = QuestionRepository()
        question = Question(
            id=None,
            area_id=area_id,
            text="¿Pregunta test?",
            active=True,
            position_weights={'Manager': 5.0}
        )
        question_repo.create(question)
        
        questions = question_repo.find_by_area_and_position(area_id, 'Manager')
        assert len(questions) >= 1

