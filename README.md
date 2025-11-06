# Sistema de Evaluación de Analistas

Sistema completo en Python con Tkinter para evaluar el desempeño de analistas en resolución de casos mediante un banco de preguntas configurable.

## Características

- **Evaluación de Analistas**: Sistema completo para evaluar analistas con preguntas personalizables
- **Perfiles de Evaluadores**: Manager, Senior Manager, Analyst, Other
- **Banco de Preguntas**: CRUD completo con penalizaciones diferenciadas por graduado/no graduado
- **Prefills por Perfil**: Configuración de respuestas por defecto según perfil
- **Cálculo Automático de Puntaje**: Inicia en 100 y resta penalizaciones según respuestas
- **Comentarios Obligatorios**: Campo obligatorio para respuestas "No"
- **Exportación**: CSV y Excel
- **Auditoría**: Registro completo de todas las acciones

## Estructura del Proyecto

```
survey/
├── main.py                        # Punto de entrada
├── requirements.txt               # Dependencias
├── README.md                      # Documentación
│
├── /src/                          # Código fuente
│   ├── /models/                   # Entidades (Profile, Question, Survey)
│   ├── /services/                 # Lógica de negocio
│   ├── /repositories/             # Acceso a datos (CRUD, SQL)
│   ├── /ui/                       # Interfaz Tkinter
│   ├── /core/                     # Utilidades (database, init_db, seeds)
│   └── __init__.py
│
├── /data/                         # Base de datos SQLite
│   └── app.db
│
├── /tests/                        # Pruebas unitarias
│   ├── test_models.py
│   ├── test_services.py
│   └── test_repositories.py
│
└── /docs/                         # Documentación técnica
    └── MIGRATION_TO_SQLSERVER.md
```

## Instalación

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd survey
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Inicializar base de datos**:
```bash
python -m src.core.init_db
```

4. **Insertar datos de ejemplo (opcional)**:
```bash
python -m src.core.seeds
```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Flujo de Evaluación

1. **Seleccionar Perfil del Evaluador**: Manager, Senior Manager, Analyst, Other
2. **Ingresar Nombre del Analista**: Nombre completo del analista a evaluar
3. **Indicar si es Graduado**: Checkbox para indicar si el analista es graduado
4. **Cargar Preguntas**: Se cargan automáticamente con prefills según el perfil
5. **Responder Preguntas**: Sí / No / N/A
   - Si responde "No", **debe** ingresar un comentario obligatorio
6. **Ver Puntaje en Tiempo Real**: El puntaje se actualiza automáticamente
7. **Guardar Evaluación**: Guarda la evaluación en la base de datos
8. **Exportar**: CSV o Excel con todas las evaluaciones

### Administración

#### Gestión de Preguntas
- **Menú → Administración → Preguntas**
- Crear, editar y eliminar preguntas
- Configurar penalizaciones para graduados y no graduados
- Establecer respuestas por defecto por perfil

#### Gestión de Perfiles
- **Menú → Administración → Perfiles**
- Crear, editar y eliminar perfiles
- Activar/desactivar perfiles

## Base de Datos

### Tablas

- **profiles**: Perfiles de evaluadores
- **questions**: Banco de preguntas
- **profile_question_defaults**: Respuestas por defecto por perfil
- **surveys**: Encuestas de evaluación
- **survey_responses**: Respuestas individuales
- **audit_log**: Log de auditoría

### Esquema SQL

El esquema está en `src/core/schema.sql` y es compatible con SQL Server para futura migración.

## Pruebas

Ejecutar todas las pruebas:

```bash
python -m unittest discover tests
```

Ejecutar pruebas específicas:

```bash
python -m unittest tests.test_models
python -m unittest tests.test_services
python -m unittest tests.test_repositories
```

## Cálculo de Puntaje

- **Puntaje inicial**: 100.0
- **Sí**: No resta nada
- **No**: Resta la penalización correspondiente (graduado o no graduado)
- **N/A**: No resta nada
- **Mínimo**: 0.0 (no puede ser negativo)

## Exportación

### CSV
- Formato: CSV estándar con encoding UTF-8
- Incluye: Todas las encuestas con sus respuestas

### Excel
- Formato: .xlsx (requiere openpyxl)
- Incluye: Todas las encuestas con sus respuestas en formato tabla

## Tecnologías

- **Python 3.8+**
- **Tkinter**: Interfaz gráfica
- **SQLite**: Base de datos
- **SQL Raw**: Consultas SQL directas (sin ORM)

## Arquitectura

- **POO**: Programación orientada a objetos
- **Repository Pattern**: Separación de acceso a datos
- **Service Layer**: Lógica de negocio separada
- **MVC**: Modelo-Vista-Controlador

## Migración a SQL Server

Ver documentación en `docs/MIGRATION_TO_SQLSERVER.md`

## Licencia

Este proyecto es de uso interno.

## Autor

Sistema desarrollado para evaluación de analistas.
