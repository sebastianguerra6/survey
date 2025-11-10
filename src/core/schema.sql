-- Esquema de base de datos para Sistema de Evaluación de Analistas
-- SQL estándar compatible con SQL Server para futura migración

-- Tabla de Perfiles
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (active IN (0, 1))
);

-- Tabla de Áreas
CREATE TABLE IF NOT EXISTS areas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (active IN (0, 1))
);

-- Tabla de Preguntas
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    penalty_graduated REAL NOT NULL DEFAULT 0.0,
    penalty_not_graduated REAL NOT NULL DEFAULT 0.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id),
    CHECK (active IN (0, 1)),
    CHECK (penalty_graduated >= 0),
    CHECK (penalty_not_graduated >= 0)
);

-- Tabla de Respuestas por Defecto por Perfil
CREATE TABLE IF NOT EXISTS profile_question_defaults (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    default_answer TEXT NOT NULL,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    UNIQUE(profile_id, question_id),
    CHECK (default_answer IN ('YES', 'NO', 'NA'))
);

-- Tabla de Casos
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES areas(id),
    UNIQUE(area_id, name),
    CHECK (active IN (0, 1))
);

-- Tabla de Encuestas
CREATE TABLE IF NOT EXISTS surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluator_profile TEXT NOT NULL,
    sid TEXT NOT NULL,
    case_id INTEGER NOT NULL,
    is_graduated INTEGER NOT NULL,
    final_score REAL NOT NULL DEFAULT 0.0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id),
    CHECK (is_graduated IN (0, 1)),
    CHECK (final_score >= 0 AND final_score <= 100)
);

-- Tabla de Respuestas de Encuestas
CREATE TABLE IF NOT EXISTS survey_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer TEXT NOT NULL,
    comment TEXT,
    penalty_applied REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id),
    CHECK (answer IN ('YES', 'NO', 'NA')),
    CHECK (penalty_applied >= 0)
);

-- Tabla de Auditoría
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    user_profile TEXT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT'))
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_areas_active ON areas(active);
CREATE INDEX IF NOT EXISTS idx_cases_active ON cases(active);
CREATE INDEX IF NOT EXISTS idx_questions_area_active ON questions(area_id, active);
CREATE INDEX IF NOT EXISTS idx_questions_active ON questions(active);
CREATE INDEX IF NOT EXISTS idx_surveys_case ON surveys(case_id);
CREATE INDEX IF NOT EXISTS idx_profile_defaults_profile ON profile_question_defaults(profile_id);
CREATE INDEX IF NOT EXISTS idx_profile_defaults_question ON profile_question_defaults(question_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_survey ON survey_responses(survey_id);
CREATE INDEX IF NOT EXISTS idx_survey_responses_question ON survey_responses(question_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);

