# Arquitectura del Sistema de Encuestas

## Visión General

El proyecto sigue una **arquitectura limpia** (Clean Architecture) con separación clara de responsabilidades, facilitando el mantenimiento, pruebas y futuras migraciones.

## Estructura de Capas

```
┌─────────────────────────────────────┐
│         Vista (Tkinter)             │  ← Capa de Presentación
│    views/main_window.py             │
│    views/admin_windows.py           │
│    views/survey_summary_window.py   │
└─────────────────────────────────────┘
              ↓ ↑
┌─────────────────────────────────────┐
│        Controladores                │  ← Capa de Lógica de Negocio
│   controllers/survey_controller.py │
│   controllers/admin_controller.py   │
└─────────────────────────────────────┘
              ↓ ↑
┌─────────────────────────────────────┐
│        Repositorios (DAO)            │  ← Capa de Acceso a Datos
│   repository/case_repository.py     │
│   repository/area_repository.py     │
│   repository/question_repository.py │
│   repository/survey_repository.py   │
└─────────────────────────────────────┘
              ↓ ↑
┌─────────────────────────────────────┐
│        Modelos (Entidades)          │  ← Capa de Dominio
│   models/case.py                    │
│   models/area.py                    │
│   models/question.py                │
│   models/survey.py                  │
└─────────────────────────────────────┘
              ↓ ↑
┌─────────────────────────────────────┐
│        Base de Datos                │  ← Capa de Persistencia
│   database/db_connection.py         │
│   database/schema.sql               │
│   database/init_db.py               │
└─────────────────────────────────────┘
```

## Principios de Diseño

### 1. Separación de Responsabilidades (SoC)

Cada capa tiene una responsabilidad única y bien definida:

- **Vistas**: Interfaz de usuario, captura de eventos, presentación de datos
- **Controladores**: Lógica de negocio, validaciones, orquestación
- **Repositorios**: Acceso a datos, consultas SQL, mapeo objeto-relacional
- **Modelos**: Estructura de datos, validaciones de dominio
- **Base de Datos**: Persistencia, esquema, conexión

### 2. Inversión de Dependencias (DIP)

Las capas superiores dependen de abstracciones (interfaces implícitas) de las capas inferiores:

- Las vistas dependen de controladores
- Los controladores dependen de repositorios
- Los repositorios dependen de la conexión a BD
- Los modelos son independientes

### 3. Repository Pattern

Los repositorios encapsulan la lógica de acceso a datos, proporcionando una interfaz uniforme:

```python
class CaseRepository:
    def create(self, case: Case) -> int
    def find_by_id(self, case_id: int) -> Optional[Case]
    def find_all(self) -> List[Case]
    def update(self, case: Case) -> bool
    def delete(self, case_id: int) -> bool
```

### 4. SQL Crudo

Se utiliza SQL estándar (no ORM) para:

- **Portabilidad**: Fácil migración a SQL Server
- **Control**: Control total sobre las consultas
- **Transparencia**: Las consultas son explícitas y verificables
- **Performance**: Sin overhead de ORM

## Flujo de Datos

### Creación de Encuesta

```
Usuario (Vista)
    ↓ Ingresa datos
MainWindow
    ↓ Valida campos
SurveyController
    ↓ Calcula puntaje
    ↓ Crea entidades
SurveyRepository
    ↓ Ejecuta SQL
DatabaseConnection
    ↓ Persiste datos
SQL Server Database
```

### Consulta de Preguntas

```
Usuario selecciona Área + Posición
    ↓
MainWindow._load_questions()
    ↓
SurveyController.load_questions(area_id, position)
    ↓
QuestionRepository.find_by_area_and_position()
    ↓
SQL JOIN con question_position_weights
    ↓
Retorna List[Question]
```

## Manejo de Errores

Cada capa maneja errores apropiados a su nivel:

- **Vista**: Muestra mensajes al usuario (messagebox)
- **Controlador**: Valida reglas de negocio, lanza excepciones descriptivas
- **Repositorio**: Maneja errores de BD, convierte a excepciones de dominio
- **Modelo**: Validaciones de datos (dataclass validators)

## SQL Estándar

El esquema SQL se entrega optimizado para SQL Server (`docs/sqlserver_schema.sql`), usando `IDENTITY`, `DATETIME2`, `BIT` y constraints explícitas.

## Extensiones Futuras

### Nuevas Funcionalidades

Para agregar nuevas funcionalidades:

1. **Nuevo modelo**: Agregar en `models/`
2. **Nuevo repositorio**: Crear en `repository/`
3. **Nuevo controlador**: Agregar lógica en `controllers/`
4. **Nueva vista**: Crear en `views/`

Ejemplo: Agregar categorías a preguntas

```python
# 1. Modelo
models/category.py

# 2. Repositorio
repository/category_repository.py

# 3. Controlador
controllers/admin_controller.py (métodos para categorías)

# 4. Vista
views/admin_windows.py (CategoryAdminWindow)
```

## Testing

Las pruebas siguen la misma estructura por capas:

- `tests/test_models.py`: Pruebas de entidades
- `tests/test_repositories.py`: Pruebas de acceso a datos
- `tests/test_controllers.py`: Pruebas de lógica de negocio

Cada capa se prueba de forma aislada usando mocks/fixtures.

## Singleton Pattern

`DatabaseConnection` usa el patrón Singleton para asegurar una única conexión a la BD:

```python
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Ventajas de esta Arquitectura

✅ **Mantenibilidad**: Código organizado y fácil de entender
✅ **Testabilidad**: Cada capa puede probarse independientemente
✅ **Escalabilidad**: Fácil agregar nuevas funcionalidades
✅ **Portabilidad**: SQL estándar facilita migración a SQL Server
✅ **Separación**: Cambios en UI no afectan lógica de negocio
✅ **Reutilización**: Repositorios pueden usarse desde diferentes controladores

