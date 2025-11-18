"""Repositorio para gestión de Encuestas."""
from typing import List, Optional
from datetime import datetime
from src.repositories.base_repository import BaseRepository
from src.models.survey import Survey, SurveyResponse


class SurveyRepository(BaseRepository):
    """Repositorio para operaciones CRUD de Encuestas."""
    
    def create(self, survey: Survey) -> int:
        """Crea una nueva encuesta y retorna su ID."""
        cursor = self.db.execute(
            """INSERT INTO surveys (evaluator_profile, sid, case_id, is_graduated, final_score, tier_id, tier_name)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                survey.evaluator_profile,
                survey.sid,
                survey.case_id,
                1 if survey.is_graduated else 0,
                survey.final_score,
                survey.tier_id,
                survey.tier_name
            )
        )
        survey_id = cursor.lastrowid
        
        # Insertar respuestas
        for response in survey.responses:
            self.create_response(survey_id, response)
        
        self.log_audit('Survey', survey_id, 'CREATE', 
                      survey.evaluator_profile, 
                      f"SID: {survey.sid}, Score: {survey.final_score}")
        return survey_id
    
    def create_response(self, survey_id: int, response: SurveyResponse) -> int:
        """Crea una respuesta de encuesta."""
        cursor = self.db.execute(
            """INSERT INTO survey_responses (survey_id, question_id, answer, comment, penalty_applied)
               VALUES (?, ?, ?, ?, ?)""",
            (
                survey_id,
                response.question_id,
                response.answer,
                response.comment,
                response.penalty_applied
            )
        )
        return cursor.lastrowid
    
    def find_by_id(self, survey_id: int) -> Optional[Survey]:
        """Busca una encuesta por ID."""
        row = self.db.fetch_one(
            """SELECT id, evaluator_profile, sid, case_id, is_graduated, final_score, tier_id, tier_name, created_at
               FROM surveys WHERE id = ?""",
            (survey_id,)
        )
        if row:
            # Cargar respuestas
            responses = self.get_responses(survey_id)
            return Survey(
                id=row['id'],
                evaluator_profile=row['evaluator_profile'],
                sid=row['sid'],
                case_id=row['case_id'],
                is_graduated=bool(row['is_graduated']),
                final_score=row['final_score'],
                tier_id=row['tier_id'],
                tier_name=row['tier_name'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                responses=responses
            )
        return None
    
    def get_responses(self, survey_id: int) -> List[SurveyResponse]:
        """Obtiene todas las respuestas de una encuesta."""
        rows = self.db.fetch_all(
            """SELECT id, question_id, answer, comment, penalty_applied
               FROM survey_responses WHERE survey_id = ?""",
            (survey_id,)
        )
        return [
            SurveyResponse(
                id=row['id'],
                survey_id=survey_id,
                question_id=row['question_id'],
                answer=row['answer'],
                comment=row['comment'],
                penalty_applied=row['penalty_applied']
            )
            for row in rows
        ]
    
    def find_all(self) -> List[Survey]:
        """Obtiene todas las encuestas."""
        rows = self.db.fetch_all(
            """SELECT id, evaluator_profile, sid, case_id, is_graduated, final_score, tier_id, tier_name, created_at
               FROM surveys ORDER BY created_at DESC"""
        )
        surveys = []
        for row in rows:
            responses = self.get_responses(row['id'])
            surveys.append(Survey(
                id=row['id'],
                evaluator_profile=row['evaluator_profile'],
                sid=row['sid'],
                case_id=row['case_id'],
                is_graduated=bool(row['is_graduated']),
                final_score=row['final_score'],
                tier_id=row['tier_id'],
                tier_name=row['tier_name'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                responses=responses
            ))
        return surveys
    
    def export_to_csv_data(self) -> List[dict]:
        """Exporta todas las encuestas a formato CSV."""
        surveys = self.find_all()
        # Obtener nombres de casos
        from src.repositories.case_repository import CaseRepository
        case_repo = CaseRepository()
        cases = {c.id: c.name for c in case_repo.find_all(active_only=False)}
        
        csv_data = []
        for survey in surveys:
            case_name = cases.get(survey.case_id, 'N/A')
            for response in survey.responses:
                csv_data.append({
                    'survey_id': survey.id,
                    'created_at': survey.created_at.isoformat() if survey.created_at else '',
                    'evaluator_profile': survey.evaluator_profile,
                    'sid': survey.sid,
                    'case_name': case_name,
                    'is_graduated': 'Sí' if survey.is_graduated else 'No',
                    'question_id': response.question_id,
                    'answer': response.answer,
                    'comment': response.comment or '',
                    'penalty_applied': response.penalty_applied,
                    'final_score': survey.final_score,
                    'tier_name': survey.tier_name or ''
                })
        return csv_data

