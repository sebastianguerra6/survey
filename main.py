"""Punto de entrada principal de la aplicación."""
import sys
import tkinter as tk
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.core.init_db import ensure_database_initialized
from src.core.seeds import ensure_seed_data
from src.ui.main_window import MainWindow


def main():
    """Función principal."""
    # Inicializar base de datos
    ensure_database_initialized()
    ensure_seed_data()
    
    # Crear interfaz
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()

