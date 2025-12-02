# Diagrama UML en Mermaid

El siguiente diagrama resume las principales relaciones entre la interfaz (`MainWindow` y módulos de administración), la capa de servicios, los repositorios y los modelos de datos.

```mermaid
classDiagram
    %% --- UI ---
    class MainWindow {
        +SurveyService survey_service
        +QuestionService question_service
        +ProfileService profile_service
        +AreaService area_service
        +CaseService case_service
        +TierService tier_service
    }
    class AreaAdminWindow
    class CaseAdminWindow
    class QuestionAdminWindow
    class ProfileAdminWindow
    class TierAdminWindow
    class SurveysViewWindow

    MainWindow ..> AreaAdminWindow : abre
    MainWindow ..> CaseAdminWindow : abre
    MainWindow ..> QuestionAdminWindow : abre
    MainWindow ..> ProfileAdminWindow : abre
    MainWindow ..> TierAdminWindow : abre
    MainWindow ..> SurveysViewWindow : abre
    MainWindow ..> SurveyService : coordina
    MainWindow ..> QuestionService : coordina
    MainWindow ..> ProfileService : coordina
    MainWindow ..> AreaService : coordina
    MainWindow ..> CaseService : coordina
    MainWindow ..> TierService : coordina

    %% --- Services & Repositories ---
    class SurveyService
    class QuestionService
    class ProfileService
    class AreaService
    class CaseService
    class TierService

    class SurveyRepository
    class QuestionRepository
    class ProfileRepository
    class AreaRepository
    class CaseRepository
    class TierRepository

    SurveyService o-- SurveyRepository
    QuestionService o-- QuestionRepository
    ProfileService o-- ProfileRepository
    AreaService o-- AreaRepository
    CaseService o-- CaseRepository
    TierService o-- TierRepository

    %% --- Models ---
    class Area {
        +int? id
        +str name
        +str? description
        +bool active
    }
    class Case {
        +int? id
        +int area_id
        +str name
        +str? description
        +bool active
    }
    class Question {
        +int? id
        +int area_id
        +str text
        +bool active
        +float penalty_graduated
        +float penalty_not_graduated
    }
    class Profile {
        +int? id
        +str name
        +bool active
    }
    class Tier {
        +int? id
        +int area_id
        +str name
        +float min_score
        +float max_score
        +str? color
        +bool active
    }
    class Survey {
        +int? id
        +str evaluator_profile
        +str sid
        +int case_id
        +bool is_graduated
        +float final_score
        +int? tier_id
        +str? tier_name
        +datetime? created_at
    }
    class SurveyResponse {
        +int? id
        +int survey_id
        +int question_id
        +str answer
        +str? comment
        +float penalty_applied
    }
    class ProfileQuestionDefault {
        +int? id
        +int profile_id
        +int question_id
        +str default_answer
    }

    SurveyRepository --> Survey
    SurveyRepository --> SurveyResponse
    QuestionRepository --> Question
    QuestionRepository --> ProfileQuestionDefault
    ProfileRepository --> Profile
    AreaRepository --> Area
    CaseRepository --> Case
    TierRepository --> Tier

    %% --- Model relationships ---
    Area "1" -- "many" Case : posee
    Area "1" -- "many" Question : define
    Area "1" -- "many" Tier : clasifica
    Case "many" -- "1" Area : pertenece
    Question "many" -- "1" Area : pertenece
    Tier "many" -- "1" Area : pertenece
    Survey "many" -- "1" Case : evalúa
    Survey "1" -- "many" SurveyResponse : agrupa
    SurveyResponse "many" -- "1" Question : responde
    ProfileQuestionDefault "many" -- "1" Profile : ajusta
    ProfileQuestionDefault "many" -- "1" Question : responde
```


