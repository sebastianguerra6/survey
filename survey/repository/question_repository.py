"""Repositorio para gestión de Preguntas."""
from typing import List, Optional, Dict
from ..database.db_connection import DatabaseConnection
from ..models.question import Question


class QuestionRepository:
    """Repositorio para operaciones CRUD de Preguntas."""
    
    def __init__(self, db: DatabaseConnection = None):
        """Inicializa el repositorio."""
        self.db = db or DatabaseConnection()
    
    def create(self, question: Question) -> int:
        """Crea una nueva pregunta y retorna su ID."""
        cursor = self.db.execute(
            "INSERT INTO questions (area_id, text, active) VALUES (?, ?, ?)",
            (question.area_id, question.text, 1 if question.active else 0)
        )
        question_id = cursor.lastrowid
        
        # Insertar pesos por posición
        self._save_position_weights(question_id, question.position_weights)
        
        return question_id
    
    def find_by_id(self, question_id: int) -> Optional[Question]:
        """Busca una pregunta por ID."""
        row = self.db.fetch_one(
            "SELECT id, area_id, text, active FROM questions WHERE id = ?",
            (question_id,)
        )
        if row:
            weights = self._load_position_weights(question_id)
            return Question(
                id=row['id'],
                area_id=row['area_id'],
                text=row['text'],
                active=bool(row['active']),
                position_weights=weights
            )
        return None
    
    def find_by_area_and_position(self, area_id: int, position: str, active_only: bool = True) -> List[Question]:
        """Busca preguntas por área y posición."""
        query = """
            SELECT q.id, q.area_id, q.text, q.active
            FROM questions q
            INNER JOIN question_position_weights qpw ON q.id = qpw.question_id
            WHERE q.area_id = ? AND qpw.position = ?
        """
        if active_only:
            query += " AND q.active = 1"
        query += " ORDER BY q.id"
        
        rows = self.db.fetch_all(query, (area_id, position))
        questions = []
        
        for row in rows:
            weights = self._load_position_weights(row['id'])
            questions.append(Question(
                id=row['id'],
                area_id=row['area_id'],
                text=row['text'],
                active=bool(row['active']),
                position_weights=weights
            ))
        
        return questions
    
    def find_all(self, active_only: bool = False) -> List[Question]:
        """Obtiene todas las preguntas."""
        query = "SELECT id, area_id, text, active FROM questions"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY area_id, id"
        
        rows = self.db.fetch_all(query)
        questions = []
        
        for row in rows:
            weights = self._load_position_weights(row['id'])
            questions.append(Question(
                id=row['id'],
                area_id=row['area_id'],
                text=row['text'],
                active=bool(row['active']),
                position_weights=weights
            ))
        
        return questions
    
    def update(self, question: Question) -> bool:
        """Actualiza una pregunta existente."""
        if question.id is None:
            raise ValueError("La pregunta debe tener un ID para ser actualizada")
        
        self.db.execute(
            "UPDATE questions SET area_id = ?, text = ?, active = ? WHERE id = ?",
            (question.area_id, question.text, 1 if question.active else 0, question.id)
        )
        
        # Actualizar pesos por posición
        self._save_position_weights(question.id, question.position_weights)
        
        return True
    
    def delete(self, question_id: int) -> bool:
        """Elimina una pregunta (soft delete: marca como inactivo)."""
        self.db.execute(
            "UPDATE questions SET active = 0 WHERE id = ?",
            (question_id,)
        )
        return True
    
    def hard_delete(self, question_id: int) -> bool:
        """Elimina físicamente una pregunta de la base de datos."""
        self.db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        return True
    
    def _load_position_weights(self, question_id: int) -> Dict[str, float]:
        """Carga los pesos por posición para una pregunta.
        
        Solo retorna las posiciones que tienen entrada en la BD.
        Si una posición no tiene entrada, no aparece en el dict.
        """
        rows = self.db.fetch_all(
            "SELECT position, penalty_value FROM question_position_weights WHERE question_id = ?",
            (question_id,)
        )
        weights = {}
        for row in rows:
            weights[row['position']] = float(row['penalty_value'])
        return weights
    
    def _save_position_weights(self, question_id: int, weights: Dict[str, float]):
        """Guarda los pesos por posición para una pregunta."""
        # Eliminar pesos existentes
        self.db.execute(
            "DELETE FROM question_position_weights WHERE question_id = ?",
            (question_id,)
        )
        
        # Insertar nuevos pesos
        for position, penalty_value in weights.items():
            self.db.execute(
                "INSERT INTO question_position_weights (question_id, position, penalty_value) VALUES (?, ?, ?)",
                (question_id, position, penalty_value)
            )

