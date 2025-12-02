"""Gestor de conexión a la base de datos SQL Server."""
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pyodbc

from src.core.config import SQLSERVER_CONNECTION_STRING


class DBExecutionResult:
    """Wrapper para exponer información adicional del cursor."""

    def __init__(self, cursor: pyodbc.Cursor, lastrowid: Optional[int]):
        self._cursor = cursor
        self.lastrowid = lastrowid

    def __getattr__(self, item):
        return getattr(self._cursor, item)


class DatabaseConnection:
    """Gestor de conexión a SQL Server usando pyodbc (Singleton)."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[pyodbc.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._init_connection()
    
    def _init_connection(self):
        """Inicializa la conexión usando la cadena configurada."""
        self._connection = pyodbc.connect(SQLSERVER_CONNECTION_STRING)
        self._connection.autocommit = False
    
    def get_connection(self) -> pyodbc.Connection:
        """Entrega la conexión activa."""
        if self._connection is None:
            self._init_connection()
        return self._connection
    
    def close(self):
        """Cierra la conexión activa."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, query: str, params: Sequence[Any] = ()) -> DBExecutionResult:
        """Ejecuta un comando SQL (INSERT/UPDATE/DELETE)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # Recuperar ID inserto si aplica
        lastrowid: Optional[int] = None
        if query.lstrip().lower().startswith("insert"):
            cursor.execute("SELECT SCOPE_IDENTITY()")
            row = cursor.fetchone()
            if row and row[0] is not None:
                try:
                    lastrowid = int(row[0])
                except (TypeError, ValueError):
                    lastrowid = None
        
        conn.commit()
        return DBExecutionResult(cursor, lastrowid)
    
    def fetch_one(self, query: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        """Retorna una fila como diccionario."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        if not row:
            return None
        columns = [col[0] for col in cursor.description]
        return {col: row[idx] for idx, col in enumerate(columns)}
    
    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        """Retorna todas las filas como diccionarios."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [{col: row[idx] for idx, col in enumerate(columns)} for row in rows]

