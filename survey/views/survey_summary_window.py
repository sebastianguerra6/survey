"""Ventana de resumen de encuesta."""
import tkinter as tk
from tkinter import ttk
from typing import Dict


class SurveySummaryWindow:
    """Ventana modal que muestra el resumen de una encuesta."""
    
    def __init__(self, parent, summary: Dict):
        """Inicializa la ventana de resumen."""
        self.window = tk.Toplevel(parent)
        self.window.title("Resumen de Encuesta")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._setup_ui(summary)
    
    def _setup_ui(self, summary: Dict):
        """Configura la interfaz con los datos del resumen."""
        # Frame principal con scroll
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información general
        info_frame = ttk.LabelFrame(main_frame, text="Información General", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_data = [
            ("Nombre:", summary['name']),
            ("SID:", summary['sid']),
            ("Caso:", summary['case']),
            ("Área:", summary['area']),
            ("Posición:", summary['position']),
            ("Fecha/Hora:", str(summary['created_at'])),
        ]
        
        for i, (label, value) in enumerate(info_data):
            ttk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2
            )
            ttk.Label(info_frame, text=str(value)).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2
            )
        
        # Puntaje
        score_frame = ttk.LabelFrame(main_frame, text="Puntaje Total", padding="10")
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        score_label = ttk.Label(
            score_frame,
            text=f"{summary['score']:.2f}",
            font=("Arial", 20, "bold"),
            foreground="blue"
        )
        score_label.pack()
        
        # Resumen de respuestas
        summary_frame = ttk.LabelFrame(main_frame, text="Resumen de Respuestas", padding="10")
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        summary_data = [
            ("Sí:", summary['yes_count']),
            ("No:", summary['no_count']),
            ("N/A:", summary['na_count']),
        ]
        
        for i, (label, value) in enumerate(summary_data):
            ttk.Label(summary_frame, text=label, font=("Arial", 10)).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2
            )
            ttk.Label(summary_frame, text=str(value), font=("Arial", 10, "bold")).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2
            )
        
        # Tabla de detalle
        detail_frame = ttk.LabelFrame(main_frame, text="Detalle de Respuestas", padding="10")
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para tabla
        columns = ('Pregunta', 'Respuesta', 'Penalización')
        tree = ttk.Treeview(detail_frame, columns=columns, show='headings', height=15)
        
        tree.heading('Pregunta', text='Pregunta')
        tree.column('Pregunta', width=400, anchor=tk.W)
        tree.heading('Respuesta', text='Respuesta')
        tree.column('Respuesta', width=100, anchor=tk.CENTER)
        tree.heading('Penalización', text='Penalización')
        tree.column('Penalización', width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Llenar tabla
        for response in summary['responses']:
            tree.insert('', tk.END, values=(
                response['question_text'],
                response['answer'],
                f"{response['penalty_applied']:.2f}"
            ))
        
        # Botón cerrar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Cerrar", command=self.window.destroy).pack()

