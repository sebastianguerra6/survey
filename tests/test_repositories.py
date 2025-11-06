"""Tests para repositorios."""
import unittest
from src.core.init_db import ensure_database_initialized
from src.repositories.profile_repository import ProfileRepository
from src.repositories.question_repository import QuestionRepository
from src.models.profile import Profile
from src.models.question import Question


class TestProfileRepository(unittest.TestCase):
    """Tests para ProfileRepository."""
    
    def setUp(self):
        """Configuración inicial."""
        ensure_database_initialized()
        self.repo = ProfileRepository()
    
    def test_create_profile(self):
        """Test creación de perfil."""
        import uuid
        unique_name = f"Test Profile {uuid.uuid4().hex[:8]}"
        profile = Profile(id=None, name=unique_name)
        profile_id = self.repo.create(profile)
        self.assertIsNotNone(profile_id)
        
        # Verificar que existe
        retrieved = self.repo.find_by_id(profile_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, unique_name)


class TestQuestionRepository(unittest.TestCase):
    """Tests para QuestionRepository."""
    
    def setUp(self):
        """Configuración inicial."""
        ensure_database_initialized()
        self.repo = QuestionRepository()
    
    def test_create_question(self):
        """Test creación de pregunta."""
        question = Question(
            id=None,
            text="¿Pregunta de prueba?",
            penalty_graduated=5.0,
            penalty_not_graduated=10.0
        )
        question_id = self.repo.create(question)
        self.assertIsNotNone(question_id)
        
        # Verificar que existe
        retrieved = self.repo.find_by_id(question_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.text, "¿Pregunta de prueba?")
    
    def test_set_default_answer(self):
        """Test establecer respuesta por defecto."""
        # Crear pregunta primero
        question = Question(id=None, text="Test Question for Default")
        question_id = self.repo.create(question)
        
        # Obtener o crear perfil (puede que ya exista)
        profile_repo = ProfileRepository()
        profiles = profile_repo.find_all(active_only=False)
        test_profile = next((p for p in profiles if p.name == "Test Profile"), None)
        
        if not test_profile:
            profile = Profile(id=None, name="Test Profile")
            profile_id = profile_repo.create(profile)
        else:
            profile_id = test_profile.id
        
        # Establecer default
        self.repo.set_default_answer(profile_id, question_id, "YES")
        
        # Verificar
        default = self.repo.get_default_answer(profile_id, question_id)
        self.assertEqual(default, "YES")


if __name__ == '__main__':
    unittest.main()

