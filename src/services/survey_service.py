"""Servicio de lógica de negocio para Encuestas."""
from typing import List, Optional
from src.models.survey import Survey, SurveyResponse
from src.models.question import Question
from src.repositories.survey_repository import SurveyRepository
from src.repositories.question_repository import QuestionRepository
from src.repositories.profile_repository import ProfileRepository
from src.repositories.case_repository import CaseRepository
from src.services.tier_service import TierService


class SurveyService:
    """Servicio para lógica de negocio de encuestas."""
    
    def __init__(self):
        """Inicializa el servicio."""
        self.survey_repo = SurveyRepository()
        self.question_repo = QuestionRepository()
        self.profile_repo = ProfileRepository()
        self.case_repo = CaseRepository()
        self.tier_service = TierService()
    
    def calculate_score(self, responses: List[SurveyResponse], is_graduated: bool, 
                       questions_map: dict) -> float:
        """Calcula el puntaje final basado en las respuestas."""
        score = 100.0
        for response in responses:
            if response.answer == 'NO':
                question = questions_map.get(response.question_id)
                if question:
                    penalty = question.get_penalty(is_graduated)
                    score -= penalty
                    response.penalty_applied = penalty
        
        # Asegurar que el mínimo sea 0
        return max(0.0, score)
    
    def create_survey(self, evaluator_profile: str, sid: str, case_id: int, is_graduated: bool,
                     responses: List[SurveyResponse]) -> int:
        """Crea una nueva encuesta y calcula el puntaje."""
        # Validar que todas las respuestas NO tengan comentario
        for response in responses:
            if response.answer == 'NO' and (not response.comment or not response.comment.strip()):
                raise ValueError(f"El comentario es obligatorio para respuestas 'NO' (Pregunta ID: {response.question_id})")
        
        # Obtener preguntas para calcular penalizaciones
        questions = self.question_repo.find_all(active_only=True)
        questions_map = {q.id: q for q in questions}
        
        # Crear encuesta temporal para calcular puntaje
        temp_survey = Survey(
            id=None,
            evaluator_profile=evaluator_profile,
            sid=sid,
            case_id=case_id,
            is_graduated=is_graduated,
            responses=responses
        )
        
        # Calcular puntaje
        final_score = self.calculate_score(responses, is_graduated, questions_map)
        temp_survey.final_score = final_score
        
        # Determinar tier
        tier = None
        case = self.case_repo.find_by_id(case_id)
        if case:
            tier = self.tier_service.get_tier_for_score(case.area_id, final_score)
        if tier:
            temp_survey.tier_id = tier.id
            temp_survey.tier_name = tier.name
        
        # Guardar encuesta
        survey_id = self.survey_repo.create(temp_survey)
        return survey_id
    
    def get_survey(self, survey_id: int) -> Optional[Survey]:
        """Obtiene una encuesta por ID."""
        return self.survey_repo.find_by_id(survey_id)
    
    def get_all_surveys(self) -> List[Survey]:
        """Obtiene todas las encuestas."""
        return self.survey_repo.find_all()

    def get_history_for_sid(self, sid: str) -> List[Survey]:
        """Obtiene el historial de encuestas para un SID."""
        if not sid:
            return []
        return self.survey_repo.find_by_sid(sid)
    
    def export_to_csv(self, filepath: str) -> bool:
        """Exporta todas las encuestas a CSV."""
        import csv
        try:
            data = self.survey_repo.export_to_csv_data()
            if not data:
                return False
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            return True
        except Exception:
            return False
    
    def export_to_excel(self, filepath: str) -> bool:
        """Exporta todas las encuestas a Excel."""
        try:
            import openpyxl
            from openpyxl import Workbook
            
            data = self.survey_repo.export_to_csv_data()
            if not data:
                return False
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Encuestas"
            
            # Headers
            if data:
                headers = list(data[0].keys())
                ws.append(headers)
                
                # Data
                for row in data:
                    ws.append([row[h] for h in headers])
            
            wb.save(filepath)
            return True
        except ImportError:
            # Si openpyxl no está instalado, intentar con csv
            return self.export_to_csv(filepath.replace('.xlsx', '.csv'))
        except Exception:
            return False

