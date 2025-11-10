"""Datos de ejemplo para inicializar la base de datos."""
from src.core.database import DatabaseConnection
from src.repositories.profile_repository import ProfileRepository
from src.repositories.area_repository import AreaRepository
from src.repositories.question_repository import QuestionRepository
from src.services.profile_service import ProfileService
from src.services.area_service import AreaService
from src.services.question_service import QuestionService


def seed_database():
    """Inserta datos de ejemplo en la base de datos."""
    profile_service = ProfileService()
    area_service = AreaService()
    question_service = QuestionService()
    
    # Crear áreas por defecto
    areas_data = [
        {"name": "Estrategia", "description": "Preguntas relacionadas con estrategia y planificación"},
        {"name": "Finanzas", "description": "Preguntas relacionadas con análisis financiero"},
        {"name": "Operaciones", "description": "Preguntas relacionadas con operaciones y procesos"},
        {"name": "Tecnología", "description": "Preguntas relacionadas con tecnología e IT"},
        {"name": "RRHH", "description": "Preguntas relacionadas con recursos humanos"},
        {"name": "Legal", "description": "Preguntas relacionadas con aspectos legales y regulatorios"},
        {"name": "Riesgos", "description": "Preguntas relacionadas con gestión de riesgos"}
    ]
    
    area_ids = {}
    for area_data in areas_data:
        try:
            area_id = area_service.create_area(
                name=area_data["name"],
                description=area_data["description"],
                active=True
            )
            area_ids[area_data["name"]] = area_id
            print(f"Área creada: {area_data['name']} (ID: {area_id})")
        except Exception as e:
            # Si ya existe, obtener su ID
            areas = area_service.get_all_areas(active_only=False)
            existing = next((a for a in areas if a.name == area_data["name"]), None)
            if existing:
                area_ids[area_data["name"]] = existing.id
                print(f"Área ya existe: {area_data['name']} (ID: {existing.id})")
    
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
    
    # Crear preguntas de ejemplo - Banco completo
    questions_data = [
        # Comprensión del Problema
        {
            "text": "¿El analista demostró comprensión adecuada del caso y sus requisitos?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿Identificó correctamente las partes interesadas y sus necesidades?",
            "penalty_graduated": 4.0,
            "penalty_not_graduated": 8.0
        },
        {
            "text": "¿Comprendió el contexto del negocio y las implicaciones del caso?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 12.0
        },
        
        # Análisis y Metodología
        {
            "text": "¿La solución propuesta es técnica y metodológicamente correcta?",
            "penalty_graduated": 10.0,
            "penalty_not_graduated": 15.0
        },
        {
            "text": "¿Utilizó un enfoque estructurado y sistemático para el análisis?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿Aplicó herramientas y técnicas apropiadas para el tipo de problema?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 11.0
        },
        {
            "text": "¿Realizó un análisis de causa raíz adecuado?",
            "penalty_graduated": 9.0,
            "penalty_not_graduated": 14.0
        },
        
        # Completitud y Profundidad
        {
            "text": "¿Se consideraron todos los aspectos relevantes del problema?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿Exploró alternativas y opciones de solución?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿Consideró las implicaciones a corto y largo plazo de la solución?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 11.0
        },
        {
            "text": "¿Incluyó un análisis de viabilidad técnica y económica?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 13.0
        },
        
        # Comunicación y Presentación
        {
            "text": "¿La comunicación de la solución fue clara y estructurada?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 8.0
        },
        {
            "text": "¿Utilizó visualizaciones y diagramas apropiados cuando fue necesario?",
            "penalty_graduated": 4.0,
            "penalty_not_graduated": 7.0
        },
        {
            "text": "¿El lenguaje utilizado fue apropiado para la audiencia objetivo?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 9.0
        },
        {
            "text": "¿Presentó la información de manera lógica y secuencial?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 8.0
        },
        
        # Gestión de Riesgos
        {
            "text": "¿Se identificaron correctamente los riesgos y limitaciones?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿Propuso estrategias de mitigación para los riesgos identificados?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿Consideró escenarios alternativos y casos extremos?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        
        # Calidad y Detalle
        {
            "text": "¿La solución propuesta es completa y detallada?",
            "penalty_graduated": 9.0,
            "penalty_not_graduated": 14.0
        },
        {
            "text": "¿Incluyó métricas y criterios de éxito medibles?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 11.0
        },
        {
            "text": "¿Proporcionó evidencia y justificación para sus recomendaciones?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 13.0
        },
        
        # Pensamiento Crítico
        {
            "text": "¿Demostró pensamiento crítico y cuestionamiento de supuestos?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿Evaluó críticamente la información disponible?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿Identificó posibles sesgos o limitaciones en su análisis?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        
        # Implementación y Práctica
        {
            "text": "¿Proporcionó un plan de implementación realista?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 13.0
        },
        {
            "text": "¿Consideró los recursos necesarios para la implementación?",
            "penalty_graduated": 7.0,
            "penalty_not_graduated": 11.0
        },
        {
            "text": "¿Definió pasos concretos y acciones específicas?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        
        # Trabajo en Equipo y Colaboración
        {
            "text": "¿Colaboró efectivamente con otros miembros del equipo?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 9.0
        },
        {
            "text": "¿Solicitó y consideró feedback de colegas y supervisores?",
            "penalty_graduated": 4.0,
            "penalty_not_graduated": 8.0
        },
        {
            "text": "¿Compartió información relevante de manera oportuna?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 9.0
        },
        
        # Innovación y Creatividad
        {
            "text": "¿Demostró creatividad en el enfoque de la solución?",
            "penalty_graduated": 6.0,
            "penalty_not_graduated": 10.0
        },
        {
            "text": "¿Propuso ideas innovadoras o mejoras al proceso actual?",
            "penalty_graduated": 5.0,
            "penalty_not_graduated": 9.0
        },
        
        # Cumplimiento y Ética
        {
            "text": "¿Consideró aspectos de cumplimiento normativo y regulatorio?",
            "penalty_graduated": 8.0,
            "penalty_not_graduated": 12.0
        },
        {
            "text": "¿Mantuvo estándares éticos en el análisis y recomendaciones?",
            "penalty_graduated": 10.0,
            "penalty_not_graduated": 15.0
        }
    ]
    
    # Asignar preguntas a áreas (distribuir entre las áreas disponibles)
    area_names_list = list(area_ids.keys())
    if not area_names_list:
        print("No hay áreas disponibles. Cree áreas primero.")
        return
    
    question_ids = []
    for i, q_data in enumerate(questions_data):
        try:
            # Distribuir preguntas entre áreas de forma circular
            area_name = area_names_list[i % len(area_names_list)]
            area_id = area_ids[area_name]
            
            q_id = question_service.create_question(
                area_id=area_id,
                text=q_data["text"],
                penalty_graduated=q_data["penalty_graduated"],
                penalty_not_graduated=q_data["penalty_not_graduated"],
                active=True
            )
            question_ids.append(q_id)
            print(f"Pregunta creada: ID {q_id} en área {area_name}")
        except Exception as e:
            print(f"Error al crear pregunta: {str(e)}")
    
    # Configurar algunos prefills de ejemplo por perfil
    if question_ids and profile_ids:
        # Manager: YES para preguntas de comprensión y comunicación
        if "Manager" in profile_ids:
            manager_id = profile_ids["Manager"]
            # Preguntas 1-3: Comprensión (YES)
            for q_id in question_ids[0:3]:
                try:
                    question_service.set_default_answer(manager_id, q_id, "YES")
                    print(f"Prefill: Manager -> Pregunta {q_id} = YES")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
            # Preguntas 12-15: Comunicación (YES)
            for q_id in question_ids[11:15] if len(question_ids) > 15 else []:
                try:
                    question_service.set_default_answer(manager_id, q_id, "YES")
                    print(f"Prefill: Manager -> Pregunta {q_id} = YES")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
        
        # Senior Manager: YES para análisis y metodología
        if "Senior Manager" in profile_ids:
            senior_manager_id = profile_ids["Senior Manager"]
            # Preguntas 4-7: Análisis y Metodología (YES)
            for q_id in question_ids[3:7] if len(question_ids) > 7 else []:
                try:
                    question_service.set_default_answer(senior_manager_id, q_id, "YES")
                    print(f"Prefill: Senior Manager -> Pregunta {q_id} = YES")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
        
        # Analyst: NA para algunas preguntas de gestión y cumplimiento
        if "Analyst" in profile_ids:
            analyst_id = profile_ids["Analyst"]
            # Preguntas 16-18: Gestión de Riesgos (NA - puede no aplicar)
            for q_id in question_ids[15:18] if len(question_ids) > 18 else []:
                try:
                    question_service.set_default_answer(analyst_id, q_id, "NA")
                    print(f"Prefill: Analyst -> Pregunta {q_id} = NA")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
            # Preguntas 33-34: Cumplimiento (NA - puede no aplicar)
            for q_id in question_ids[32:34] if len(question_ids) > 34 else []:
                try:
                    question_service.set_default_answer(analyst_id, q_id, "NA")
                    print(f"Prefill: Analyst -> Pregunta {q_id} = NA")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
        
        # Other: Mixto
        if "Other" in profile_ids:
            other_id = profile_ids["Other"]
            # Algunas preguntas básicas con YES
            for q_id in question_ids[0:2] if len(question_ids) > 2 else []:
                try:
                    question_service.set_default_answer(other_id, q_id, "YES")
                    print(f"Prefill: Other -> Pregunta {q_id} = YES")
                except Exception as e:
                    print(f"Error al configurar prefill: {str(e)}")
    
    print("\nDatos de ejemplo insertados correctamente.")


if __name__ == '__main__':
    from src.core.init_db import ensure_database_initialized
    ensure_database_initialized()
    seed_database()

