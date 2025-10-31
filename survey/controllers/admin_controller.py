"""Controlador para gestión de administración."""
from typing import List, Optional
import csv
from ..repository.case_repository import CaseRepository
from ..repository.area_repository import AreaRepository
from ..repository.question_repository import QuestionRepository
from ..models.case import Case
from ..models.area import Area
from ..models.question import Question


class AdminController:
    """Controlador para lógica de negocio de administración."""
    
    def __init__(self):
        """Inicializa el controlador."""
        self.case_repo = CaseRepository()
        self.area_repo = AreaRepository()
        self.question_repo = QuestionRepository()
    
    # Gestión de Casos
    def create_case(self, name: str, active: bool = True) -> int:
        """Crea un nuevo caso."""
        case = Case(id=None, name=name, active=active)
        return self.case_repo.create(case)
    
    def get_all_cases(self, active_only: bool = False) -> List[Case]:
        """Obtiene todos los casos."""
        return self.case_repo.find_all(active_only=active_only)
    
    def get_case(self, case_id: int) -> Optional[Case]:
        """Obtiene un caso por ID."""
        return self.case_repo.find_by_id(case_id)
    
    def update_case(self, case_id: int, name: str, active: bool = True) -> bool:
        """Actualiza un caso."""
        case = Case(id=case_id, name=name, active=active)
        return self.case_repo.update(case)
    
    def delete_case(self, case_id: int) -> bool:
        """Elimina un caso."""
        return self.case_repo.delete(case_id)
    
    # Gestión de Áreas
    def create_area(self, name: str, active: bool = True) -> int:
        """Crea un nuevo área."""
        area = Area(id=None, name=name, active=active)
        return self.area_repo.create(area)
    
    def get_all_areas(self, active_only: bool = False) -> List[Area]:
        """Obtiene todas las áreas."""
        return self.area_repo.find_all(active_only=active_only)
    
    def get_area(self, area_id: int) -> Optional[Area]:
        """Obtiene un área por ID."""
        return self.area_repo.find_by_id(area_id)
    
    def update_area(self, area_id: int, name: str, active: bool = True) -> bool:
        """Actualiza un área."""
        area = Area(id=area_id, name=name, active=active)
        return self.area_repo.update(area)
    
    def delete_area(self, area_id: int) -> bool:
        """Elimina un área."""
        return self.area_repo.delete(area_id)
    
    # Gestión de Preguntas
    def create_question(
        self,
        area_id: int,
        text: str,
        active: bool = True,
        position_weights: Optional[dict] = None
    ) -> int:
        """Crea una nueva pregunta.
        
        position_weights debe contener solo las posiciones aplicables a esta pregunta.
        Si una posición no está en el dict, esa pregunta NO aparecerá para esa posición.
        """
        if position_weights is None:
            position_weights = {}  # Por defecto, no aplica a ninguna posición
        
        if not position_weights:
            raise ValueError("Debe especificar al menos una posición aplicable")
        
        question = Question(
            id=None,
            area_id=area_id,
            text=text,
            active=active,
            position_weights=position_weights
        )
        return self.question_repo.create(question)
    
    def get_all_questions(self, active_only: bool = False) -> List[Question]:
        """Obtiene todas las preguntas."""
        return self.question_repo.find_all(active_only=active_only)
    
    def get_question(self, question_id: int) -> Optional[Question]:
        """Obtiene una pregunta por ID."""
        return self.question_repo.find_by_id(question_id)
    
    def update_question(
        self,
        question_id: int,
        area_id: int,
        text: str,
        active: bool = True,
        position_weights: Optional[dict] = None
    ) -> bool:
        """Actualiza una pregunta."""
        if position_weights is None:
            question = self.question_repo.find_by_id(question_id)
            if question:
                position_weights = question.position_weights
        
        question = Question(
            id=question_id,
            area_id=area_id,
            text=text,
            active=active,
            position_weights=position_weights
        )
        return self.question_repo.update(question)
    
    def delete_question(self, question_id: int) -> bool:
        """Elimina una pregunta."""
        return self.question_repo.delete(question_id)
    
    # Importar/Exportar CSV
    def export_questions_to_csv(self, filepath: str):
        """Exporta todas las preguntas a CSV."""
        questions = self.get_all_questions(active_only=False)
        areas = {area.id: area.name for area in self.get_all_areas()}
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Área', 'Texto', 'Activa',
                'Penalización Manager', 'Penalización Senior Manager',
                'Penalización Analyst', 'Penalización Senior Analyst'
            ])
            
            for question in questions:
                writer.writerow([
                    question.id,
                    areas.get(question.area_id, 'N/A'),
                    question.text,
                    'Sí' if question.active else 'No',
                    question.position_weights.get('Manager', 0.0),
                    question.position_weights.get('Senior Manager', 0.0),
                    question.position_weights.get('Analyst', 0.0),
                    question.position_weights.get('Senior Analyst', 0.0)
                ])
    
    def import_questions_from_csv(self, filepath: str) -> int:
        """Importa preguntas desde CSV. Retorna número de preguntas importadas."""
        imported_count = 0
        areas_map = {area.name: area.id for area in self.get_all_areas()}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    area_name = row['Área']
                    area_id = areas_map.get(area_name)
                    if not area_id:
                        continue
                    
                    text = row['Texto']
                    active = row.get('Activa', 'Sí').lower() in ('sí', 'si', 'yes', '1', 'true')
                    
                    position_weights = {
                        'Manager': float(row.get('Penalización Manager', 0.0)),
                        'Senior Manager': float(row.get('Penalización Senior Manager', 0.0)),
                        'Analyst': float(row.get('Penalización Analyst', 0.0)),
                        'Senior Analyst': float(row.get('Penalización Senior Analyst', 0.0))
                    }
                    
                    self.create_question(area_id, text, active, position_weights)
                    imported_count += 1
                except Exception as e:
                    print(f"Error importando pregunta: {e}")
                    continue
        
        return imported_count

