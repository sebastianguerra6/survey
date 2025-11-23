"""Setup script para el paquete de encuestas."""
from setuptools import setup, find_packages

setup(
    name="survey",
    version="1.0.0",
    description="Sistema de Encuestas de Análisis de Caso",
    author="Desarrollador",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Dependencias declaradas en requirements.txt (pyodbc, openpyxl, etc.)
    ],
    entry_points={
        'console_scripts': [
            'survey=survey.main:main',
        ],
    },
)

