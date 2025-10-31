-- Esquema de base de datos para aplicación de encuestas
-- SQL estándar compatible con SQL Server para futura migración

-- Tabla de Casos
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Áreas
CREATE TABLE IF NOT EXISTS areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Preguntas
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id),
    CHECK (active IN (0, 1))
);

-- Tabla de Pesos/Penalizaciones por Posición para cada Pregunta
CREATE TABLE IF NOT EXISTS question_position_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL,
    position TEXT NOT NULL,
    penalty_value REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE(question_id, position),
    CHECK (penalty_value >= 0),
    CHECK (position IN ('Manager', 'Senior Manager', 'Analyst', 'Senior Analyst'))
);

-- Tabla de Encuestas
CREATE TABLE IF NOT EXISTS surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sid TEXT NOT NULL,
    case_id INTEGER NOT NULL,
    area_id INTEGER NOT NULL,
    position TEXT NOT NULL,
    score REAL NOT NULL DEFAULT 100.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id),
    FOREIGN KEY (area_id) REFERENCES areas(id),
    CHECK (score >= 0 AND score <= 100),
    CHECK (position IN ('Manager', 'Senior Manager', 'Analyst', 'Senior Analyst'))
);

-- Tabla de Respuestas de Encuestas
CREATE TABLE IF NOT EXISTS survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    penalty_applied REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    CHECK (answer IN ('Yes', 'No', 'N/A')),
    CHECK (penalty_applied >= 0)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_questions_area_active ON questions(area_id, active);
CREATE INDEX IF NOT EXISTS idx_question_weights_question ON question_position_weights(question_id);
CREATE INDEX IF NOT EXISTS idx_surveys_case ON surveys(case_id);
CREATE INDEX IF NOT EXISTS idx_surveys_area ON surveys(area_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey ON survey_responses(survey_id);

