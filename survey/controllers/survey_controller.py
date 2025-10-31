"""Controlador para gestión de encuestas."""
from typing import List, Optional, Dict
from datetime import datetime
from ..models.survey import Survey, SurveyResponse
from ..models.question import Question
from ..repository.survey_repository import SurveyRepository
from ..repository.question_repository import QuestionRepository
from ..repository.case_repository import CaseRepository
from ..repository.area_repository import AreaRepository


class SurveyController:
    """Controlador para lógica de negocio de encuestas."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.survey_repo = SurveyRepository()
        self.question_repo = QuestionRepository()
        self.case_repo = CaseRepository()
        self.area_repo = AreaRepository()
    
    def load_questions(self, area_id: int, position: str) -> List[Question]:
        """Carga las preguntas activas para un área y posición específicos."""
        return self.question_repo.find_by_area_and_position(area_id, position, active_only=True)
    
    def calculate_score(self, questions: List[Question], answers: Dict[int, str], position: str) -> float:
        """Calcula el puntaje basado en las respuestas."""
        initial_score = 100.0
        total_penalty = 0.0
        
        for question in questions:
            answer = answers.get(question.id)
            if answer == 'No':
                penalty = question.get_penalty_for_position(position)
                total_penalty += penalty
        
        final_score = initial_score - total_penalty
        return max(0.0, min(100.0, final_score))
    
    def save_survey(
        self,
        name: str,
        sid: str,
        case_id: int,
        area_id: int,
        position: str,
        answers: Dict[int, str]
    ) -> int:
        """Guarda una encuesta completa."""
        # Validar datos requeridos
        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")
        if not sid or not sid.strip():
            raise ValueError("El SID es obligatorio")
        if case_id is None:
            raise ValueError("El caso es obligatorio")
        if area_id is None:
            raise ValueError("El área es obligatoria")
        if not position:
            raise ValueError("La posición es obligatoria")
        
        # Cargar preguntas
        questions = self.load_questions(area_id, position)
        if not questions:
            raise ValueError(f"No hay preguntas activas para el área y posición seleccionados")
        
        # Calcular puntaje
        score = self.calculate_score(questions, answers, position)
        
        # Crear encuesta
        survey = Survey(
            id=None,
            name=name.strip(),
            sid=sid.strip(),
            case_id=case_id,
            area_id=area_id,
            position=position,
            score=score,
            created_at=datetime.now(),
            responses=[]
        )
        
        # Crear respuestas
        for question in questions:
            answer = answers.get(question.id, 'N/A')
            penalty = 0.0
            if answer == 'No':
                penalty = question.get_penalty_for_position(position)
            
            response = SurveyResponse(
                id=None,
                survey_id=0,  # Se asignará después
                question_id=question.id,
                answer=answer,
                penalty_applied=penalty
            )
            survey.responses.append(response)
        
        # Guardar en BD
        survey_id = self.survey_repo.create(survey)
        return survey_id
    
    def get_survey_summary(self, survey_id: int) -> Dict:
        """Obtiene un resumen de una encuesta."""
        survey = self.survey_repo.find_by_id(survey_id)
        if not survey:
            raise ValueError("Encuesta no encontrada")
        
        case = self.case_repo.find_by_id(survey.case_id)
        area = self.area_repo.find_by_id(survey.area_id)
        
        # Contar respuestas
        yes_count = sum(1 for r in survey.responses if r.answer == 'Yes')
        no_count = sum(1 for r in survey.responses if r.answer == 'No')
        na_count = sum(1 for r in survey.responses if r.answer == 'N/A')
        
        # Cargar textos de preguntas
        question_texts = {}
        for response in survey.responses:
            question = self.question_repo.find_by_id(response.question_id)
            if question:
                question_texts[response.question_id] = question.text
        
        return {
            'survey_id': survey.id,
            'name': survey.name,
            'sid': survey.sid,
            'case': case.name if case else 'N/A',
            'area': area.name if area else 'N/A',
            'position': survey.position,
            'score': survey.score,
            'created_at': survey.created_at,
            'yes_count': yes_count,
            'no_count': no_count,
            'na_count': na_count,
            'responses': [
                {
                    'question_text': question_texts.get(r.question_id, 'N/A'),
                    'answer': r.answer,
                    'penalty_applied': r.penalty_applied
                }
                for r in survey.responses
            ]
        }
    
    def export_survey_to_csv(self, survey_id: int, filepath: str):
        """Exporta una encuesta a CSV."""
        import csv
        summary = self.get_survey_summary(survey_id)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Encabezados generales
            writer.writerow(['Campo', 'Valor'])
            writer.writerow(['Nombre', summary['name']])
            writer.writerow(['SID', summary['sid']])
            writer.writerow(['Caso', summary['case']])
            writer.writerow(['Área', summary['area']])
            writer.writerow(['Posición', summary['position']])
            writer.writerow(['Puntaje', summary['score']])
            writer.writerow(['Fecha/Hora', summary['created_at']])
            writer.writerow([])
            writer.writerow(['Resumen de Respuestas'])
            writer.writerow(['Sí', summary['yes_count']])
            writer.writerow(['No', summary['no_count']])
            writer.writerow(['N/A', summary['na_count']])
            writer.writerow([])
            
            # Detalle de respuestas
            writer.writerow(['Detalle de Respuestas'])
            writer.writerow(['Pregunta', 'Respuesta', 'Penalización'])
            for resp in summary['responses']:
                writer.writerow([
                    resp['question_text'],
                    resp['answer'],
                    resp['penalty_applied']
                ])

