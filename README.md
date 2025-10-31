# Sistema de Encuestas de Análisis de Caso

Sistema completo desarrollado en Python con Tkinter para la gestión de encuestas de análisis de caso, utilizando SQLite como base de datos con SQL estándar para futura migración a SQL Server.

## Características

- **Interfaz gráfica** con Tkinter
- **Base de datos SQLite** con SQL estándar
- **Arquitectura limpia** (MVC/Repository)
- **Gestión completa de encuestas** con cálculo automático de puntajes
- **Administración** de Casos, Áreas y Preguntas
- **Exportación** de resultados a CSV

## Requisitos

- Python 3.8 o superior
- Tkinter (incluido con Python estándar)
- SQLite3 (incluido con Python estándar)

## Instalación

1. Clonar o descargar el proyecto
2. Instalar dependencias opcionales (para pruebas):

```bash
pip install -r requirements.txt
```

## Estructura del Proyecto

```
survey/
├── survey/
│   ├── models/              # Modelos de datos (entidades)
│   │   ├── case.py
│   │   ├── area.py
│   │   ├── question.py
│   │   └── survey.py
│   ├── database/            # Capa de base de datos
│   │   ├── db_connection.py
│   │   ├── init_db.py
│   │   └── schema.sql
│   ├── repository/         # Capa Repository/DAO
│   │   ├── case_repository.py
│   │   ├── area_repository.py
│   │   ├── question_repository.py
│   │   └── survey_repository.py
│   ├── controllers/         # Controladores (lógica de negocio)
│   │   ├── survey_controller.py
│   │   └── admin_controller.py
│   ├── views/               # Vistas Tkinter
│   │   ├── main_window.py
│   │   ├── admin_windows.py
│   │   └── survey_summary_window.py
│   └── main.py             # Punto de entrada
├── tests/                   # Pruebas unitarias
├── data/                    # Base de datos SQLite (se crea automáticamente)
├── requirements.txt
└── README.md
```

## Uso

### Ejecutar la aplicación

```bash
python -m survey
```

O directamente:

```bash
python survey/main.py
```

### Inicialización

La primera vez que se ejecuta la aplicación, se crea automáticamente:
- La estructura de la base de datos
- Las 7 áreas por defecto: Estrategia, Finanzas, Operaciones, Tecnología, RRHH, Legal, Riesgos

### Flujo de trabajo

1. **Administración inicial** (opcional):
   - Menú → Administración → Casos: Crear casos
   - Menú → Administración → Preguntas: Crear preguntas con sus penalizaciones por posición

2. **Crear encuesta**:
   - Ingresar Nombre y SID (obligatorios)
   - Seleccionar Caso (obligatorio)
   - Seleccionar Posición: Manager, Senior Manager, Analyst, Senior Analyst (obligatorio)
   - Seleccionar Área (obligatorio)
   - Clic en "Cargar Preguntas"
   - Responder las preguntas (Sí/No/N/A)
   - El puntaje se actualiza en tiempo real
   - Clic en "Guardar Encuesta"
   - Ver resumen y exportar si se desea

## Funcionalidades

### Gestión de Encuestas

- **Puntaje inicial**: 100 puntos
- **Respuestas**:
  - Sí → 0 penalización
  - No → resta el valor de penalización configurado para la posición
  - N/A → 0 penalización
- **Puntaje mínimo**: 0

### Administración

#### Casos (CRUD)
- Crear, editar y eliminar casos
- Marcar como activo/inactivo

#### Áreas (CRUD)
- Crear, editar y eliminar áreas
- 7 áreas por defecto
- Marcar como activo/inactivo

#### Preguntas (CRUD)
- Crear, editar y eliminar preguntas
- Asignar a un área
- Configurar penalizaciones por posición (4 valores numéricos ≥ 0)
- Marcar como activa/inactiva
- **Importar/Exportar CSV** del banco de preguntas

### Exportación

- Exportar resultado de encuesta a CSV
- Incluye: datos generales, puntaje, resumen de respuestas y detalle completo

## Reglas de Negocio

1. Una encuesta = una persona + un caso + un área + preguntas de esa área
2. El set de preguntas mostrado depende solo de Área y Posición
3. No es necesario completar otras áreas
4. El puntaje mínimo es 0
5. Todos los campos marcados como obligatorios deben completarse

## Arquitectura

El proyecto sigue una arquitectura limpia con separación de responsabilidades:

- **Models**: Entidades de dominio
- **Database**: Conexión y esquema de BD
- **Repository**: Acceso a datos con SQL crudo (DAO pattern)
- **Controllers**: Lógica de negocio
- **Views**: Interfaz de usuario (Tkinter)

### SQL Estándar

El código SQL está escrito siguiendo estándares para facilitar futura migración a SQL Server:
- Sin funciones específicas de SQLite
- Uso de tipos de datos estándar
- Constraints estándar (CHECK, FOREIGN KEY, UNIQUE)
- Índices para optimización

## Pruebas

Ejecutar pruebas:

```bash
pytest tests/
```

Con cobertura:

```bash
pytest tests/ --cov=survey --cov-report=html
```

## Base de Datos

La base de datos se guarda en: `data/survey.db`

### Esquema

- **cases**: Casos
- **areas**: Áreas
- **questions**: Preguntas
- **question_position_weights**: Penalizaciones por posición para cada pregunta
- **surveys**: Encuestas
- **survey_responses**: Respuestas individuales

## Documentación

La documentación del código está incluida en los docstrings de cada módulo y función.

## Desarrollo

### Agregar nuevas funcionalidades

1. Modelos: Agregar entidades en `models/`
2. Repository: Crear repositorio en `repository/`
3. Controller: Agregar lógica en `controllers/`
4. View: Crear vista en `views/`

### Migración a SQL Server

Para migrar a SQL Server en el futuro:
1. Cambiar `AUTOINCREMENT` por `IDENTITY(1,1)`
2. Cambiar `INTEGER` por `INT`
3. Ajustar tipos de fecha/hora según necesidad
4. Actualizar cadena de conexión en `db_connection.py`

## Licencia

Este proyecto es de uso interno.

## Autor

Desarrollado como aplicación de análisis de caso con arquitectura limpia y buenas prácticas.

