"""Repositorio para gestión de Preguntas."""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.question import Question


class QuestionRepository(BaseRepository):
    """Repositorio para operaciones CRUD de Preguntas."""
    
    def create(self, question: Question) -> int:
        """Crea una nueva pregunta y retorna su ID."""
        cursor = self.db.execute(
            """INSERT INTO questions (area_id, text, active, penalty_graduated, penalty_not_graduated)
               VALUES (?, ?, ?, ?, ?)""",
            (
                question.area_id,
                question.text,
                1 if question.active else 0,
                question.penalty_graduated,
                question.penalty_not_graduated
            )
        )
        question_id = cursor.lastrowid
        self.log_audit('Question', question_id, 'CREATE', details=f"Texto: {question.text[:50]}...")
        return question_id
    
    def find_by_id(self, question_id: int) -> Optional[Question]:
        """Busca una pregunta por ID."""
        row = self.db.fetch_one(
            """SELECT id, area_id, text, active, penalty_graduated, penalty_not_graduated
               FROM questions WHERE id = ?""",
            (question_id,)
        )
        if row:
            return Question(
                id=row['id'],
                area_id=row['area_id'],
                text=row['text'],
                active=bool(row['active']),
                penalty_graduated=row['penalty_graduated'],
                penalty_not_graduated=row['penalty_not_graduated']
            )
        return None
    
    def find_all(self, active_only: bool = False, area_id: Optional[int] = None) -> List[Question]:
        """Obtiene todas las preguntas, opcionalmente filtradas por área."""
        query = """SELECT id, area_id, text, active, penalty_graduated, penalty_not_graduated
                   FROM questions"""
        conditions = []
        if active_only:
            conditions.append("active = 1")
        if area_id is not None:
            conditions.append("area_id = ?")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"
        
        params = (area_id,) if area_id is not None else ()
        rows = self.db.fetch_all(query, params)
        return [
            Question(
                id=row['id'],
                area_id=row['area_id'],
                text=row['text'],
                active=bool(row['active']),
                penalty_graduated=row['penalty_graduated'],
                penalty_not_graduated=row['penalty_not_graduated']
            )
            for row in rows
        ]
    
    def update(self, question: Question) -> bool:
        """Actualiza una pregunta existente."""
        if question.id is None:
            raise ValueError("La pregunta debe tener un ID para ser actualizada")
        
        self.db.execute(
            """UPDATE questions SET area_id = ?, text = ?, active = ?, penalty_graduated = ?, penalty_not_graduated = ?
               WHERE id = ?""",
            (
                question.area_id,
                question.text,
                1 if question.active else 0,
                question.penalty_graduated,
                question.penalty_not_graduated,
                question.id
            )
        )
        self.log_audit('Question', question.id, 'UPDATE', details=f"Texto: {question.text[:50]}...")
        return True
    
    def delete(self, question_id: int) -> bool:
        """Elimina una pregunta (soft delete)."""
        self.db.execute("UPDATE questions SET active = 0 WHERE id = ?", (question_id,))
        self.log_audit('Question', question_id, 'DELETE')
        return True
    
    def get_default_answer(self, profile_id: int, question_id: int) -> Optional[str]:
        """Obtiene la respuesta por defecto para un perfil y pregunta."""
        row = self.db.fetch_one(
            """SELECT default_answer FROM profile_question_defaults
               WHERE profile_id = ? AND question_id = ?""",
            (profile_id, question_id)
        )
        if row:
            return row['default_answer']
        return None
    
    def set_default_answer(self, profile_id: int, question_id: int, default_answer: str) -> bool:
        """Establece la respuesta por defecto para un perfil y pregunta."""
        # Eliminar si existe
        self.db.execute(
            """DELETE FROM profile_question_defaults
               WHERE profile_id = ? AND question_id = ?""",
            (profile_id, question_id)
        )
        # Insertar nuevo
        self.db.execute(
            """INSERT INTO profile_question_defaults (profile_id, question_id, default_answer)
               VALUES (?, ?, ?)""",
            (profile_id, question_id, default_answer)
        )
        return True
    
    def get_defaults_for_profile(self, profile_id: int) -> dict:
        """Obtiene todas las respuestas por defecto para un perfil."""
        rows = self.db.fetch_all(
            """SELECT question_id, default_answer FROM profile_question_defaults
               WHERE profile_id = ?""",
            (profile_id,)
        )
        return {row['question_id']: row['default_answer'] for row in rows}

