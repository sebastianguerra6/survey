"""Configuración centralizada para la conexión SQL Server."""
import os

SQLSERVER_CONNECTION_STRING = os.getenv(
    "SQLSERVER_CONNECTION_STRING",
    (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=PCSEBASTIAN\\SQLEXPRESS01;"
        "DATABASE=EvaluationDB;"
        "Trusted_Connection=yes;"
    ),
)

