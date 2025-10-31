"""Módulo de conexión a base de datos."""
import sqlite3
import os
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """Gestor de conexión a la base de datos SQLite."""
    
    _instance: Optional['DatabaseConnection'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls):
        """Patrón Singleton para una única conexión."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión si no existe."""
        if self._connection is None:
            self._init_connection()
    
    def _init_connection(self):
        """Inicializa la conexión a la base de datos."""
        db_path = self._get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._connection = sqlite3.connect(
            db_path,
            check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row
    
    @staticmethod
    def _get_db_path() -> str:
        """Obtiene la ruta del archivo de base de datos."""
        # El directorio base es el padre del directorio survey/
        base_dir = Path(__file__).parent.parent.parent
        return str(base_dir / 'data' / 'survey.db')
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtiene la conexión activa."""
        if self._connection is None:
            self._init_connection()
        return self._connection
    
    def close(self):
        """Cierra la conexión."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute_script(self, script: str):
        """Ejecuta un script SQL."""
        conn = self.get_connection()
        conn.executescript(script)
        conn.commit()
    
    def execute(self, query: str, params: tuple = ()):
        """Ejecuta una consulta SQL."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Ejecuta una consulta y retorna una fila."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = ()) -> list:
        """Ejecuta una consulta y retorna todas las filas."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

