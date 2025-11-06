"""Datos de ejemplo para inicializar la base de datos."""
from src.core.database import DatabaseConnection
from src.repositories.profile_repository import ProfileRepository
from src.repositories.question_repository import QuestionRepository
from src.services.profile_service import ProfileService
from src.services.question_service import QuestionService


def seed_database():
    """Inserta datos de ejemplo en la base de datos."""
    profile_service = ProfileService()
    question_service = QuestionService()
    
    # Crear perfiles por defecto
    profiles_data = [
        "Manager",
        "Senior Manager",
        "Analyst",
        "Other"
    ]
    
    profile_ids = {}
    for profile_name in profiles_data:
        try:
            profile_id = profile_service.create_profile(name=profile_name, active=True)
            profile_ids[profile_name] = profile_id
            print(f"Perfil creado: {profile_name} (ID: {profile_id})")
        except Exception as e:
            # Si ya existe, obtener su ID
            profiles = profile_service.get_all_profiles(active_only=False)
            existing = next((p for p in profiles if p.name == profile_name), None)
            if existing:
                profile_ids[profile_name] = existing.id
                print(f"Perfil ya existe: {profile_name} (ID: {existing.id})")
    
    # Crear preguntas de ejemplo
    questions_data = [
        {
            "text": "¿El analista demostró comprensión adecuada del caso?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿La solución propuesta es técnica y metodológicamente correcta?",
            "penalty_graduated": 10.0,
            "penalty_not_graduated": 15.0
        },
        {
            "text": "¿Se consideraron todos los aspectos relevantes del problema?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿La comunicación de la solución fue clara y estructurada?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 8.0
        },
        {
            "text": "¿Se identificaron correctamente los riesgos y limitaciones?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 10.0
        }
    ]
    
    question_ids = []
    for q_data in questions_data:
        try:
            q_id = question_service.create_question(
                text=q_data["text"],
                penalty_graduated=q_data["penalty_graduated"],
                penalty_not_graduated=q_data["penalty_not_graduated"],
                active=True
            )
            question_ids.append(q_id)
            print(f"Pregunta creada: ID {q_id}")
        except Exception as e:
            print(f"Error al crear pregunta: {str(e)}")
    
    # Configurar algunos prefills de ejemplo
    if question_ids and profile_ids:
        # Manager: YES para primeras preguntas
        if "Manager" in profile_ids:
            manager_id = profile_ids["Manager"]
            for i, q_id in enumerate(question_ids[:2]):
                try:
                    question_service.set_default_answer(manager_id, q_id, "YES")
                    print(f"Prefill configurado: Manager -> Pregunta {q_id} = YES")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
        
        # Analyst: NA para algunas preguntas
        if "Analyst" in profile_ids:
            analyst_id = profile_ids["Analyst"]
            for i, q_id in enumerate(question_ids[2:4]):
                try:
                    question_service.set_default_answer(analyst_id, q_id, "NA")
                    print(f"Prefill configurado: Analyst -> Pregunta {q_id} = NA")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
    
    print("\nDatos de ejemplo insertados correctamente.")


if __name__ == '__main__':
    from src.core.init_db import ensure_database_initialized
    ensure_database_initialized()
    seed_database()

