"""Punto de entrada principal de la aplicación."""
import sys
import os
from pathlib import Path
import tkinter as tk

# Agregar el directorio raíz al PYTHONPATH para imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from survey.database.init_db import init_database
from survey.views.main_window import MainWindow


def main():
    """Función principal."""
    # Inicializar base de datos si no existe
    db_path = Path(__file__).parent.parent / 'data' / 'survey.db'
    if not db_path.exists():
        print("Inicializando base de datos...")
        init_database()
    else:
        # Si la BD ya existe, asegurar que tenga preguntas
        from survey.database.init_db import add_default_questions
        try:
            add_default_questions()
        except Exception as e:
            print(f"Nota: {e}")
    
    # Crear ventana principal
    root = tk.Tk()
    app = MainWindow(root)
    
    # Ejecutar aplicación
    root.mainloop()


if __name__ == '__main__':
    main()

