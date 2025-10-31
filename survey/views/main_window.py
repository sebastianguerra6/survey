"""Ventana principal de la aplicación."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Optional
from ..controllers.survey_controller import SurveyController
from ..controllers.admin_controller import AdminController
from .admin_windows import AreaAdminWindow, QuestionAdminWindow
from .survey_summary_window import SurveySummaryWindow


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self, root: tk.Tk):
        """Inicializa la ventana principal."""
        self.root = root
        self.root.title("Sistema de Encuestas de Análisis de Caso")
        self.root.geometry("900x700")
        
        self.survey_controller = SurveyController()
        self.admin_controller = AdminController()
        
        self.questions: list = []
        self.current_answers: Dict[int, str] = {}
        self.current_score: float = 100.0
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Administración", menu=admin_menu)
        admin_menu.add_command(label="Áreas", command=self._open_area_admin)
        admin_menu.add_command(label="Preguntas", command=self._open_question_admin)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos superiores
        top_frame = ttk.LabelFrame(main_frame, text="Datos de la Encuesta", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Nombre
        ttk.Label(top_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(top_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # SID
        ttk.Label(top_frame, text="SID:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.sid_entry = ttk.Entry(top_frame, width=30)
        self.sid_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Caso (editable para escribir directamente)
        ttk.Label(top_frame, text="Caso:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.case_combo = ttk.Combobox(top_frame, width=27, state="normal")
        self.case_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Posición
        ttk.Label(top_frame, text="Posición:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.position_combo = ttk.Combobox(
            top_frame,
            values=["Manager", "Senior Manager", "Analyst", "Senior Analyst"],
            width=27,
            state="readonly"
        )
        self.position_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # Área
        ttk.Label(top_frame, text="Área:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(top_frame, width=27, state="readonly")
        self.area_combo.grid(row=2, column=1, padx=5, pady=5)
        
        # Botón Cargar Preguntas
        self.load_btn = ttk.Button(top_frame, text="Cargar Preguntas", command=self._load_questions)
        self.load_btn.grid(row=2, column=2, columnspan=2, padx=5, pady=5)
        
        # Puntaje actual
        score_frame = ttk.Frame(main_frame)
        score_frame.pack(fill=tk.X, pady=(0, 10))
        self.score_label = ttk.Label(
            score_frame,
            text="Puntaje Actual: 100.0",
            font=("Arial", 12, "bold"),
            foreground="blue"
        )
        self.score_label.pack()
        
        # Panel de preguntas con scroll
        questions_frame = ttk.LabelFrame(main_frame, text="Preguntas", padding="10")
        questions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas y scrollbar para preguntas
        canvas = tk.Canvas(questions_frame)
        scrollbar = ttk.Scrollbar(questions_frame, orient="vertical", command=canvas.yview)
        self.questions_scroll_frame = ttk.Frame(canvas)
        
        self.questions_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.questions_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.questions_container = self.questions_scroll_frame
        
        # Botones inferiores
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.save_btn = ttk.Button(button_frame, text="Guardar Encuesta", command=self._save_survey)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = ttk.Button(button_frame, text="Exportar Resultado", command=self._export_survey)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        self.saved_survey_id: Optional[int] = None
    
    def _load_data(self):
        """Carga datos iniciales en los combos."""
        # Cargar casos (como sugerencias para el combo editable)
        cases = self.admin_controller.get_all_cases(active_only=True)
        case_names = [case.name for case in cases]
        self.case_combo['values'] = case_names
        
        # Cargar áreas
        areas = self.admin_controller.get_all_areas(active_only=True)
        area_names = [area.name for area in areas]
        self.area_combo['values'] = area_names
    
    def _load_questions(self):
        """Carga las preguntas según área y posición seleccionadas."""
        # Validar campos requeridos
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un Área")
            return
        if not self.position_combo.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione una Posición")
            return
        
        # Obtener IDs
        area_name = self.area_combo.get()
        position = self.position_combo.get()
        
        areas = self.admin_controller.get_all_areas(active_only=True)
        area_id = next((a.id for a in areas if a.name == area_name), None)
        
        if not area_id:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        # Cargar preguntas
        try:
            self.questions = self.survey_controller.load_questions(area_id, position)
            
            if not self.questions:
                messagebox.showinfo("Información", "No hay preguntas activas para el área y posición seleccionados")
                return
            
            self._render_questions()
            self._update_score()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar preguntas: {str(e)}")
    
    def _render_questions(self):
        """Renderiza las preguntas en el panel."""
        # Limpiar contenedor
        for widget in self.questions_container.winfo_children():
            widget.destroy()
        
        self.current_answers = {}
        
        # Crear pregunta por pregunta
        for question in self.questions:
            q_frame = ttk.LabelFrame(self.questions_container, text=f"Pregunta #{question.id}", padding="10")
            q_frame.pack(fill=tk.X, pady=5, padx=5)
            
            ttk.Label(q_frame, text=question.text, wraplength=800).pack(anchor=tk.W, pady=(0, 5))
            
            # RadioButtons para respuestas
            answer_var = tk.StringVar(value="N/A")
            self.current_answers[question.id] = "N/A"
            
            def on_answer_change(question_id, var):
                def callback():
                    self.current_answers[question_id] = var.get()
                    self._update_score()
                return callback
            
            callback = on_answer_change(question.id, answer_var)
            
            answer_frame = ttk.Frame(q_frame)
            answer_frame.pack(anchor=tk.W)
            
            ttk.Radiobutton(
                answer_frame,
                text="Sí",
                variable=answer_var,
                value="Yes",
                command=callback
            ).pack(side=tk.LEFT, padx=10)
            
            ttk.Radiobutton(
                answer_frame,
                text="No",
                variable=answer_var,
                value="No",
                command=callback
            ).pack(side=tk.LEFT, padx=10)
            
            ttk.Radiobutton(
                answer_frame,
                text="N/A",
                variable=answer_var,
                value="N/A",
                command=callback
            ).pack(side=tk.LEFT, padx=10)
            
            # Mostrar penalización
            penalty = question.get_penalty_for_position(self.position_combo.get())
            if penalty > 0:
                ttk.Label(
                    answer_frame,
                    text=f"(Penalización si No: {penalty})",
                    foreground="red"
                ).pack(side=tk.LEFT, padx=10)
    
    def _update_score(self):
        """Actualiza el puntaje actual."""
        if not self.questions or not self.position_combo.get():
            self.current_score = 100.0
        else:
            self.current_score = self.survey_controller.calculate_score(
                self.questions,
                self.current_answers,
                self.position_combo.get()
            )
        
        self.score_label.config(text=f"Puntaje Actual: {self.current_score:.2f}")
    
    def _save_survey(self):
        """Guarda la encuesta."""
        # Validar campos obligatorios
        if not self.name_entry.get().strip():
            messagebox.showwarning("Advertencia", "El Nombre es obligatorio")
            return
        if not self.sid_entry.get().strip():
            messagebox.showwarning("Advertencia", "El SID es obligatorio")
            return
        if not self.case_combo.get().strip():
            messagebox.showwarning("Advertencia", "El Caso es obligatorio")
            return
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El Área es obligatoria")
            return
        if not self.position_combo.get():
            messagebox.showwarning("Advertencia", "La Posición es obligatoria")
            return
        
        if not self.questions:
            messagebox.showwarning("Advertencia", "Debe cargar preguntas antes de guardar")
            return
        
        try:
            # Obtener o crear caso
            case_name = self.case_combo.get().strip()
            area_name = self.area_combo.get()
            
            # Buscar caso existente
            cases = self.admin_controller.get_all_cases(active_only=True)
            case_id = next((c.id for c in cases if c.name == case_name), None)
            
            # Si no existe, crearlo automáticamente
            if not case_id:
                try:
                    case_id = self.admin_controller.create_case(case_name, active=True)
                    # Actualizar el combo con el nuevo caso
                    self._load_data()
                    self.case_combo.set(case_name)
                except Exception as e:
                    messagebox.showerror("Error", f"Error al crear caso: {str(e)}")
                    return
            
            # Obtener área
            areas = self.admin_controller.get_all_areas(active_only=True)
            area_id = next((a.id for a in areas if a.name == area_name), None)
            
            if not area_id:
                messagebox.showerror("Error", "Área no encontrada")
                return
            
            # Guardar encuesta
            survey_id = self.survey_controller.save_survey(
                name=self.name_entry.get().strip(),
                sid=self.sid_entry.get().strip(),
                case_id=case_id,
                area_id=area_id,
                position=self.position_combo.get(),
                answers=self.current_answers
            )
            
            self.saved_survey_id = survey_id
            
            # Bloquear edición
            self.name_entry.config(state='disabled')
            self.sid_entry.config(state='disabled')
            self.case_combo.config(state='disabled')
            self.area_combo.config(state='disabled')
            self.position_combo.config(state='disabled')
            self.load_btn.config(state='disabled')
            self.save_btn.config(state='disabled')
            
            # Mostrar resumen
            summary = self.survey_controller.get_survey_summary(survey_id)
            summary_window = SurveySummaryWindow(self.root, summary)
            
            messagebox.showinfo("Éxito", f"Encuesta guardada correctamente. ID: {survey_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar encuesta: {str(e)}")
    
    def _export_survey(self):
        """Exporta la encuesta a CSV."""
        if not self.saved_survey_id:
            messagebox.showwarning("Advertencia", "Debe guardar la encuesta antes de exportar")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.survey_controller.export_survey_to_csv(self.saved_survey_id, filepath)
                messagebox.showinfo("Éxito", f"Encuesta exportada a {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def _open_area_admin(self):
        """Abre ventana de administración de áreas."""
        AreaAdminWindow(self.root, self.admin_controller, callback=self._load_data)
    
    def _open_question_admin(self):
        """Abre ventana de administración de preguntas."""
        QuestionAdminWindow(self.root, self.admin_controller)

