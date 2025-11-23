/* ============================================================================
   Script de creación de base de datos para SQL Server
   Proyecto: Sistema de Evaluación de Analistas
   Uso: Ejecutar en SQL Server Management Studio o sqlcmd
============================================================================ */

IF DB_ID('EvaluationDB') IS NULL
BEGIN
    CREATE DATABASE EvaluationDB;
END
GO

USE EvaluationDB;
GO

/* ---------------------------------------------------------------------------
   Tabla: profiles
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.profiles', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.profiles (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE,
        active BIT NOT NULL CONSTRAINT DF_profiles_active DEFAULT (1),
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_profiles_created DEFAULT (SYSUTCDATETIME())
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: areas
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.areas', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.areas (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE,
        description NVARCHAR(MAX) NULL,
        active BIT NOT NULL CONSTRAINT DF_areas_active DEFAULT (1),
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_areas_created DEFAULT (SYSUTCDATETIME())
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: questions
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.questions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.questions (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        area_id INT NOT NULL,
        [text] NVARCHAR(MAX) NOT NULL,
        active BIT NOT NULL CONSTRAINT DF_questions_active DEFAULT (1),
        penalty_graduated DECIMAL(6,2) NOT NULL CONSTRAINT DF_questions_pen_grad DEFAULT (0.00),
        penalty_not_graduated DECIMAL(6,2) NOT NULL CONSTRAINT DF_questions_pen_not_grad DEFAULT (0.00),
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_questions_created DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT FK_questions_area FOREIGN KEY(area_id) REFERENCES dbo.areas(id),
        CONSTRAINT CK_questions_pen_grad CHECK (penalty_graduated >= 0),
        CONSTRAINT CK_questions_pen_not_grad CHECK (penalty_not_graduated >= 0)
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: profile_question_defaults
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.profile_question_defaults', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.profile_question_defaults (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        profile_id INT NOT NULL,
        question_id INT NOT NULL,
        default_answer CHAR(2) NOT NULL,
        CONSTRAINT FK_defaults_profile FOREIGN KEY(profile_id) REFERENCES dbo.profiles(id) ON DELETE CASCADE,
        CONSTRAINT FK_defaults_question FOREIGN KEY(question_id) REFERENCES dbo.questions(id) ON DELETE CASCADE,
        CONSTRAINT UQ_defaults_profile_question UNIQUE (profile_id, question_id),
        CONSTRAINT CK_defaults_answers CHECK (default_answer IN ('YES', 'NO', 'NA'))
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: cases
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.cases', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.cases (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        area_id INT NOT NULL,
        name NVARCHAR(255) NOT NULL,
        description NVARCHAR(MAX) NULL,
        active BIT NOT NULL CONSTRAINT DF_cases_active DEFAULT (1),
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_cases_created DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT FK_cases_area FOREIGN KEY(area_id) REFERENCES dbo.areas(id),
        CONSTRAINT UQ_cases_area_name UNIQUE (area_id, name)
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: tiers
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.tiers', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.tiers (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        area_id INT NOT NULL,
        name NVARCHAR(255) NOT NULL,
        min_score DECIMAL(5,2) NOT NULL,
        max_score DECIMAL(5,2) NOT NULL,
        description NVARCHAR(MAX) NULL,
        color NVARCHAR(32) NULL,
        active BIT NOT NULL CONSTRAINT DF_tiers_active DEFAULT (1),
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_tiers_created DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT FK_tiers_area FOREIGN KEY(area_id) REFERENCES dbo.areas(id) ON DELETE CASCADE,
        CONSTRAINT UQ_tiers_area_name UNIQUE (area_id, name),
        CONSTRAINT CK_tiers_score CHECK (min_score >= 0 AND max_score <= 100 AND min_score <= max_score)
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: surveys
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.surveys', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.surveys (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        evaluator_profile NVARCHAR(255) NOT NULL,
        sid NVARCHAR(255) NOT NULL,
        case_id INT NOT NULL,
        is_graduated BIT NOT NULL,
        final_score DECIMAL(5,2) NOT NULL CONSTRAINT DF_surveys_score DEFAULT (0.00),
        tier_id INT NULL,
        tier_name NVARCHAR(255) NULL,
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_surveys_created DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT FK_surveys_case FOREIGN KEY(case_id) REFERENCES dbo.cases(id),
        CONSTRAINT FK_surveys_tier FOREIGN KEY(tier_id) REFERENCES dbo.tiers(id),
        CONSTRAINT CK_surveys_score CHECK (final_score BETWEEN 0 AND 100)
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: survey_responses
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.survey_responses', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.survey_responses (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        survey_id INT NOT NULL,
        question_id INT NOT NULL,
        answer CHAR(2) NOT NULL,
        comment NVARCHAR(MAX) NULL,
        penalty_applied DECIMAL(6,2) NOT NULL CONSTRAINT DF_responses_penalty DEFAULT (0.00),
        CONSTRAINT FK_responses_survey FOREIGN KEY(survey_id) REFERENCES dbo.surveys(id) ON DELETE CASCADE,
        CONSTRAINT FK_responses_question FOREIGN KEY(question_id) REFERENCES dbo.questions(id),
        CONSTRAINT CK_responses_answer CHECK (answer IN ('YES', 'NO', 'NA')),
        CONSTRAINT CK_responses_penalty CHECK (penalty_applied >= 0)
    );
END
GO

/* ---------------------------------------------------------------------------
   Tabla: audit_log
--------------------------------------------------------------------------- */
IF OBJECT_ID('dbo.audit_log', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.audit_log (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        entity_type NVARCHAR(255) NOT NULL,
        entity_id INT NULL,
        action NVARCHAR(32) NOT NULL,
        user_profile NVARCHAR(255) NULL,
        details NVARCHAR(MAX) NULL,
        created_at DATETIME2(0) NOT NULL CONSTRAINT DF_audit_created DEFAULT (SYSUTCDATETIME()),
        CONSTRAINT CK_audit_action CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT'))
    );
END
GO

/* ---------------------------------------------------------------------------
   Índices
--------------------------------------------------------------------------- */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_areas_active')
    CREATE INDEX idx_areas_active ON dbo.areas(active);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_cases_active')
    CREATE INDEX idx_cases_active ON dbo.cases(active);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_tiers_area')
    CREATE INDEX idx_tiers_area ON dbo.tiers(area_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_tiers_area_score')
    CREATE INDEX idx_tiers_area_score ON dbo.tiers(area_id, min_score, max_score);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_questions_area_active')
    CREATE INDEX idx_questions_area_active ON dbo.questions(area_id, active);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_surveys_case')
    CREATE INDEX idx_surveys_case ON dbo.surveys(case_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_profile_defaults_profile')
    CREATE INDEX idx_profile_defaults_profile ON dbo.profile_question_defaults(profile_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_profile_defaults_question')
    CREATE INDEX idx_profile_defaults_question ON dbo.profile_question_defaults(question_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_survey_responses_survey')
    CREATE INDEX idx_survey_responses_survey ON dbo.survey_responses(survey_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_survey_responses_question')
    CREATE INDEX idx_survey_responses_question ON dbo.survey_responses(question_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_audit_log_entity')
    CREATE INDEX idx_audit_log_entity ON dbo.audit_log(entity_type, entity_id);

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'idx_audit_log_created')
    CREATE INDEX idx_audit_log_created ON dbo.audit_log(created_at);
GO

