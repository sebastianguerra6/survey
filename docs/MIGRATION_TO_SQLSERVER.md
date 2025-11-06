# Guía de Migración a SQL Server

Esta guía explica cómo migrar la base de datos de SQLite a SQL Server.

## Diferencias Principales

### 1. Tipos de Datos

| SQLite | SQL Server |
|--------|-----------|
| INTEGER | INT o BIGINT |
| TEXT | NVARCHAR(MAX) o VARCHAR |
| REAL | FLOAT o DECIMAL |
| DATETIME | DATETIME2 o DATETIME |

### 2. Auto Increment

- **SQLite**: `INTEGER PRIMARY KEY AUTOINCREMENT`
- **SQL Server**: `INT IDENTITY(1,1) PRIMARY KEY`

### 3. CHECK Constraints

- **SQLite**: Soporta CHECK
- **SQL Server**: Soporta CHECK (mismo comportamiento)

### 4. CREATE TABLE IF NOT EXISTS

- **SQLite**: Soporta directamente
- **SQL Server**: Requiere verificación previa o usar `IF NOT EXISTS` (SQL Server 2016+)

## Script de Migración

### Paso 1: Crear Base de Datos en SQL Server

```sql
CREATE DATABASE EvaluationDB;
GO

USE EvaluationDB;
GO
```

### Paso 2: Convertir Schema

El archivo `src/core/schema.sql` debe ser convertido. Ejemplo de conversión:

```sql
-- Tabla de Perfiles (SQL Server)
CREATE TABLE profiles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL UNIQUE,
    active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Tabla de Preguntas (SQL Server)
CREATE TABLE questions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    text NVARCHAR(MAX) NOT NULL,
    active BIT NOT NULL DEFAULT 1,
    penalty_graduated FLOAT NOT NULL DEFAULT 0.0,
    penalty_not_graduated FLOAT NOT NULL DEFAULT 0.0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Resto de tablas siguiendo el mismo patrón...
```

### Paso 3: Modificar DatabaseConnection

Crear nuevo archivo `src/core/database_sqlserver.py`:

```python
"""Gestor de conexión a SQL Server."""
import pyodbc
from typing import Optional


class DatabaseConnection:
    """Gestor de conexión a SQL Server."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[pyodbc.Connection] = None
    
    def __init__(self, connection_string: str):
        """Inicializa la conexión."""
        self.connection_string = connection_string
        if self._connection is None:
            self._init_connection()
    
    def _init_connection(self):
        """Inicializa la conexión."""
        self._connection = pyodbc.connect(self.connection_string)
    
    def get_connection(self):
        """Obtiene la conexión activa."""
        return self._connection
    
    # ... resto de métodos similares
```

### Paso 4: Configuración

Crear archivo de configuración `src/core/config.py`:

```python
"""Configuración de la aplicación."""
import os

# Tipo de base de datos
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' o 'sqlserver'

# SQLite
SQLITE_DB_PATH = 'data/app.db'

# SQL Server
SQLSERVER_CONNECTION_STRING = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=your_server;'
    'DATABASE=EvaluationDB;'
    'UID=your_user;'
    'PWD=your_password'
)
```

### Paso 5: Migrar Datos

Script Python para migrar datos:

```python
"""Script de migración de datos."""
from src.core.database import DatabaseConnection as SQLiteDB
from src.core.database_sqlserver import DatabaseConnection as SQLServerDB
from src.core.config import SQLSERVER_CONNECTION_STRING

# Conectar a ambas bases
sqlite_db = SQLiteDB()
sqlserver_db = SQLServerDB(SQLSERVER_CONNECTION_STRING)

# Migrar perfiles
profiles = sqlite_db.fetch_all("SELECT * FROM profiles")
for profile in profiles:
    sqlserver_db.execute(
        "INSERT INTO profiles (name, active, created_at) VALUES (?, ?, ?)",
        (profile['name'], profile['active'], profile['created_at'])
    )

# Repetir para otras tablas...
```

## Cambios Necesarios en el Código

### 1. DatabaseConnection Factory

```python
# src/core/database_factory.py
from src.core.config import DB_TYPE
from src.core.database import DatabaseConnection as SQLiteConnection
from src.core.database_sqlserver import DatabaseConnection as SQLServerConnection

def get_database():
    """Factory para obtener la conexión según configuración."""
    if DB_TYPE == 'sqlserver':
        return SQLServerConnection(SQLSERVER_CONNECTION_STRING)
    else:
        return SQLiteConnection()
```

### 2. Ajustes en Queries

Algunas funciones pueden necesitar ajustes:

- **LIMIT**: SQL Server usa `TOP` o `OFFSET ... FETCH`
- **Date Functions**: SQL Server usa `GETDATE()` en lugar de `CURRENT_TIMESTAMP`
- **String Functions**: Algunas funciones de string pueden diferir

## Testing

Después de la migración:

1. Verificar que todas las tablas existen
2. Ejecutar tests unitarios
3. Probar todas las funcionalidades de la aplicación
4. Verificar integridad de datos

## Rollback

Si es necesario volver a SQLite:

1. Mantener backup de SQLite
2. Revertir cambios en `DatabaseConnection`
3. Restaurar base de datos SQLite

## Notas Importantes

- **Transacciones**: SQL Server maneja transacciones de forma diferente
- **Concurrencia**: SQL Server tiene mejor manejo de concurrencia
- **Performance**: SQL Server puede ser más rápido para grandes volúmenes
- **Escalabilidad**: SQL Server es mejor para múltiples usuarios concurrentes

## Recursos

- [SQL Server Documentation](https://docs.microsoft.com/en-us/sql/)
- [PyODBC Documentation](https://github.com/mkleehammer/pyodbc)
- [SQLite to SQL Server Migration Guide](https://docs.microsoft.com/en-us/sql/relational-databases/migration/migrate-from-sqlite-to-sql-server)

