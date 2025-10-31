# Guía de Inicio Rápido

## Instalación Rápida

1. **Asegúrate de tener Python 3.8+ instalado**

2. **Clona o descarga el proyecto**

3. **Instala dependencias (opcional para pruebas)**:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecutar la Aplicación

### Opción 1: Como módulo Python
```bash
python -m survey
```

### Opción 2: Ejecutar directamente
```bash
python survey/main.py
```

### Opción 3: Instalar como paquete (opcional)
```bash
pip install -e .
survey
```

## Primera Ejecución

En la primera ejecución:
1. Se crea automáticamente la base de datos en `data/survey.db`
2. Se crean las 7 áreas por defecto:
   - Estrategia
   - Finanzas
   - Operaciones
   - Tecnología
   - RRHH
   - Legal
   - Riesgos

## Configuración Inicial Recomendada

### 1. Crear Casos
- Menú → Administración → Casos
- Clic en "Crear" para agregar casos

### 2. Crear Preguntas
- Menú → Administración → Preguntas
- Crear preguntas asignadas a cada área
- Configurar penalizaciones por posición:
  - Manager
  - Senior Manager
  - Analyst
  - Senior Analyst

**Ejemplo de penalización:**
- Si una pregunta tiene penalización 5.0 para Manager
- Y la respuesta es "No"
- El puntaje se reduce en 5.0 (de 100 a 95)

## Flujo de Trabajo

### Crear una Encuesta

1. **Llenar datos personales**:
   - Nombre (obligatorio)
   - SID (obligatorio)

2. **Seleccionar configuración**:
   - Caso (obligatorio)
   - Posición (obligatorio): Manager, Senior Manager, Analyst, Senior Analyst
   - Área (obligatorio)

3. **Cargar preguntas**:
   - Clic en "Cargar Preguntas"
   - Se muestran las preguntas activas para esa área y posición

4. **Responder preguntas**:
   - Seleccionar Sí / No / N/A para cada pregunta
   - El puntaje se actualiza en tiempo real

5. **Guardar encuesta**:
   - Clic en "Guardar Encuesta"
   - Ver resumen
   - Opcional: Exportar a CSV

## Exportación

### Exportar Encuesta Individual
- Después de guardar una encuesta
- Clic en "Exportar Resultado"
- Seleccionar ubicación para guardar CSV

### Exportar Banco de Preguntas
- Menú → Administración → Preguntas
- Clic en "Exportar CSV"
- Seleccionar ubicación

### Importar Banco de Preguntas
- Menú → Administración → Preguntas
- Clic en "Importar CSV"
- Seleccionar archivo CSV con formato:
  ```
  ID,Área,Texto,Activa,Penalización Manager,...
  ```

## Solución de Problemas

### Error: "No module named 'survey'"
- Ejecuta desde el directorio raíz del proyecto
- O instala el paquete: `pip install -e .`

### Error: Base de datos no se crea
- Verifica permisos de escritura en el directorio
- Asegúrate de que el directorio `data/` puede crearse

### Error: "No hay preguntas activas"
- Asegúrate de haber creado preguntas en Administración
- Verifica que las preguntas estén marcadas como activas
- Confirma que la pregunta tiene penalización configurada para la posición seleccionada

## Estructura de Base de Datos

La base de datos se encuentra en: `data/survey.db`

### Tablas Principales

- **cases**: Casos del sistema
- **areas**: Áreas (7 por defecto)
- **questions**: Preguntas con texto
- **question_position_weights**: Penalizaciones por posición
- **surveys**: Encuestas completas
- **survey_responses**: Respuestas individuales

## Ejecutar Pruebas

```bash
# Todas las pruebas
pytest

# Con cobertura
pytest --cov=survey --cov-report=html

# Pruebas específicas
pytest tests/test_models.py
```

## Migración Futura a SQL Server

El SQL está escrito en estándar para facilitar migración:

1. Actualizar `database/db_connection.py` con conexión SQL Server
2. Modificar `schema.sql`:
   - `AUTOINCREMENT` → `IDENTITY(1,1)`
   - Ajustar tipos según necesidad
3. Las consultas SQL crudas facilitan la migración

## Soporte

Para problemas o preguntas, revisa:
- `README.md`: Documentación completa
- `ARCHITECTURE.md`: Detalles de arquitectura
- Código: Docstrings en cada módulo

