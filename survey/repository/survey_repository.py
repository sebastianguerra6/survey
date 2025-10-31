"""Repositorio para gestión de Encuestas."""
from typing import List, Optional
from datetime import datetime
from ..database.db_connection import DatabaseConnection
from ..models.survey import Survey, SurveyResponse


class SurveyRepository:
    """Repositorio para operaciones CRUD de Encuestas."""
    
    def __init__(self, db: DatabaseConnection = None):
        """Inicializa el repositorio."""
        self.db = db or DatabaseConnection()
    
    def create(self, survey: Survey) -> int:
        """Crea una nueva encuesta y retorna su ID."""
        cursor = self.db.execute(
            """INSERT INTO surveys (name, sid, case_id, area_id, position, score, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                survey.name,
                survey.sid,
                survey.case_id,
                survey.area_id,
                survey.position,
                survey.score,
                survey.created_at
            )
        )
        survey_id = cursor.lastrowid
        
        # Guardar respuestas
        for response in survey.responses:
            self._create_response(survey_id, response)
        
        return survey_id
    
    def find_by_id(self, survey_id: int) -> Optional[Survey]:
        """Busca una encuesta por ID."""
        row = self.db.fetch_one(
            """SELECT id, name, sid, case_id, area_id, position, score, created_at
               FROM surveys WHERE id = ?""",
            (survey_id,)
        )
        if row:
            responses = self._find_responses_by_survey_id(survey_id)
            return Survey(
                id=row['id'],
                name=row['name'],
                sid=row['sid'],
                case_id=row['case_id'],
                area_id=row['area_id'],
                position=row['position'],
                score=float(row['score']),
                created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at'],
                responses=responses
            )
        return None
    
    def find_all(self) -> List[Survey]:
        """Obtiene todas las encuestas."""
        rows = self.db.fetch_all(
            """SELECT id, name, sid, case_id, area_id, position, score, created_at
               FROM surveys ORDER BY created_at DESC"""
        )
        surveys = []
        
        for row in rows:
            responses = self._find_responses_by_survey_id(row['id'])
            surveys.append(Survey(
                id=row['id'],
                name=row['name'],
                sid=row['sid'],
                case_id=row['case_id'],
                area_id=row['area_id'],
                position=row['position'],
                score=float(row['score']),
                created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at'],
                responses=responses
            ))
        
        return surveys
    
    def _create_response(self, survey_id: int, response: SurveyResponse) -> int:
        """Crea una respuesta de encuesta."""
        cursor = self.db.execute(
            """INSERT INTO survey_responses (survey_id, question_id, answer, penalty_applied)
               VALUES (?, ?, ?, ?)""",
            (survey_id, response.question_id, response.answer, response.penalty_applied)
        )
        return cursor.lastrowid
    
    def _find_responses_by_survey_id(self, survey_id: int) -> List[SurveyResponse]:
        """Obtiene todas las respuestas de una encuesta."""
        rows = self.db.fetch_all(
            """SELECT id, survey_id, question_id, answer, penalty_applied
               FROM survey_responses WHERE survey_id = ?""",
            (survey_id,)
        )
        return [
            SurveyResponse(
                id=row['id'],
                survey_id=row['survey_id'],
                question_id=row['question_id'],
                answer=row['answer'],
                penalty_applied=float(row['penalty_applied'])
            )
            for row in rows
        ]

