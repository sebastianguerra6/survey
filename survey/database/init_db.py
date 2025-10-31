"""Inicialización de la base de datos."""
import sqlite3
from pathlib import Path
from .db_connection import DatabaseConnection


def init_database():
    """Inicializa la base de datos con el esquema y datos por defecto."""
    db = DatabaseConnection()
    
    # Crear esquema
    schema_path = Path(__file__).parent / 'schema.sql'
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    db.execute_script(schema_sql)
    
    # Insertar áreas por defecto
    area_ids = _insert_default_areas(db)
    
    # Insertar preguntas de ejemplo para cada área
    _insert_default_questions(db, area_ids)
    
    print("Base de datos inicializada correctamente.")


def add_default_questions():
    """Agrega preguntas de ejemplo a las áreas existentes (sin recrear la BD)."""
    db = DatabaseConnection()
    
    # Obtener IDs de áreas existentes
    area_rows = db.fetch_all("SELECT id, name FROM areas WHERE active = 1")
    area_ids = {row['name']: row['id'] for row in area_rows}
    
    # Insertar preguntas de ejemplo para cada área
    _insert_default_questions(db, area_ids)
    
    print(f"Preguntas agregadas para {len(area_ids)} áreas.")


def _insert_default_areas(db: DatabaseConnection) -> dict:
    """Inserta las 7 áreas por defecto y retorna un diccionario con los IDs."""
    default_areas = [
        'Estrategia',
        'Finanzas',
        'Operaciones',
        'Tecnología',
        'RRHH',
        'Legal',
        'Riesgos'
    ]
    
    area_ids = {}
    for area_name in default_areas:
        try:
            cursor = db.execute(
                "INSERT INTO areas (name, active) VALUES (?, ?)",
                (area_name, 1)
            )
            # Obtener el ID del área insertada
            row = db.fetch_one("SELECT id FROM areas WHERE name = ?", (area_name,))
            if row:
                area_ids[area_name] = row['id']
        except sqlite3.IntegrityError:
            # Área ya existe, obtener su ID
            row = db.fetch_one("SELECT id FROM areas WHERE name = ?", (area_name,))
            if row:
                area_ids[area_name] = row['id']
    
    return area_ids


def _insert_default_questions(db: DatabaseConnection, area_ids: dict):
    """Inserta preguntas de ejemplo para cada área."""
    # Definir preguntas por área
    questions_by_area = {
        'Estrategia': [
            ("¿La estrategia está claramente definida y documentada?", {'Manager': 5.0, 'Senior Manager': 7.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
            ("¿Existe un plan de ejecución detallado?", {'Manager': 4.0, 'Senior Manager': 6.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
            ("¿Se han identificado los riesgos estratégicos?", {'Manager': 3.0, 'Senior Manager': 5.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
        ],
        'Finanzas': [
            ("¿El presupuesto está aprobado y disponible?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Los controles financieros están implementados?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
            ("¿Los reportes financieros se generan regularmente?", {'Manager': 3.0, 'Senior Manager': 4.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
        ],
        'Operaciones': [
            ("¿Los procesos operativos están documentados?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
            ("¿Existen métricas de desempeño operativo?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
            ("¿Los recursos operativos son suficientes?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
        ],
        'Tecnología': [
            ("¿La infraestructura tecnológica es adecuada?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Existen controles de seguridad implementados?", {'Manager': 6.0, 'Senior Manager': 7.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Los sistemas cumplen con los requisitos?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
        ],
        'RRHH': [
            ("¿El equipo tiene las competencias necesarias?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Existe un plan de capacitación?", {'Manager': 3.0, 'Senior Manager': 4.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
            ("¿La estructura organizacional es adecuada?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 2.0, 'Senior Analyst': 3.0}),
        ],
        'Legal': [
            ("¿Se cumplen todos los requisitos legales?", {'Manager': 6.0, 'Senior Manager': 7.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Los contratos están revisados y aprobados?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
            ("¿Se han identificado los riesgos legales?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
        ],
        'Riesgos': [
            ("¿Se ha realizado un análisis de riesgos completo?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 4.0, 'Senior Analyst': 5.0}),
            ("¿Existen planes de mitigación para los riesgos críticos?", {'Manager': 5.0, 'Senior Manager': 6.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
            ("¿Los controles de riesgo están implementados?", {'Manager': 4.0, 'Senior Manager': 5.0, 'Analyst': 3.0, 'Senior Analyst': 4.0}),
        ]
    }
    
    # Insertar preguntas
    for area_name, questions in questions_by_area.items():
        area_id = area_ids.get(area_name)
        if not area_id:
            continue
        
        for question_text, position_weights in questions:
            # Verificar si la pregunta ya existe
            existing = db.fetch_one(
                "SELECT id FROM questions WHERE area_id = ? AND text = ?",
                (area_id, question_text)
            )
            if existing:
                continue  # Ya existe, saltar
            
            # Insertar pregunta
            db.execute(
                "INSERT INTO questions (area_id, text, active) VALUES (?, ?, ?)",
                (area_id, question_text, 1)
            )
            # Obtener el ID de la pregunta insertada
            question_row = db.fetch_one(
                "SELECT id FROM questions WHERE area_id = ? AND text = ?",
                (area_id, question_text)
            )
            if not question_row:
                continue
            
            question_id = question_row['id']
            
            # Insertar pesos por posición (solo para las posiciones que tienen valor > 0 o están definidas)
            for position, penalty in position_weights.items():
                db.execute(
                    "INSERT INTO question_position_weights (question_id, position, penalty_value) VALUES (?, ?, ?)",
                    (question_id, position, penalty)
                )


if __name__ == '__main__':
    init_database()

