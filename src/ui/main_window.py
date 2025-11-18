"""Ventana principal de evaluación."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional
from src.services.survey_service import SurveyService
from src.services.question_service import QuestionService
from src.services.profile_service import ProfileService
from src.services.area_service import AreaService
from src.services.case_service import CaseService
from src.services.tier_service import TierService
from src.models.survey import SurveyResponse
from src.models.question import Question


class MainWindow:
    """Ventana principal para crear evaluaciones."""
    
    def __init__(self, root: tk.Tk):
        """Inicializa la ventana principal."""
        self.root = root
        self.root.title("Sistema de Evaluación de Analistas")
        self.root.geometry("1100x780")
        
        self.colors = {
            "background": "#fff1f2",
            "card": "#fffdfd",
            "accent": "#dc2626",
            "accent_dark": "#b91c1c",
            "border": "#fecdd3",
            "text_muted": "#9f1239",
            "success": "#b91c1c",
            "warning": "#dc2626",
            "danger": "#f87171",
        }
        self._configure_styles()
        
        self.survey_service = SurveyService()
        self.question_service = QuestionService()
        self.profile_service = ProfileService()
        self.area_service = AreaService()
        self.case_service = CaseService()
        self.tier_service = TierService()
        
        self.questions: List[Question] = []
        self.current_responses: Dict[int, SurveyResponse] = {}
        self.answer_vars: Dict[int, tk.StringVar] = {}
        self.comment_entries: Dict[int, tk.Text] = {}
        self.current_score: float = 100.0
        self.current_tier = None
        self.selected_area_id: Optional[int] = None
        
        self._setup_ui()
        # Cargar datos después de que la UI esté completamente inicializada
        self.root.after(100, self._load_data)
    
    def _configure_styles(self):
        """Configura estilos personalizados para una apariencia moderna."""
        style = ttk.Style(self.root)
        self.root.configure(bg=self.colors["background"])
        
        for preferred in ("vista", "clam", "default"):
            if preferred in style.theme_names():
                style.theme_use(preferred)
                break
        
        style.configure("Main.TFrame", background=self.colors["background"])
        style.configure("Header.TFrame", background=self.colors["background"])
        style.configure(
            "HeaderTitle.TLabel",
            background=self.colors["background"],
            font=("Segoe UI", 22, "bold"),
            foreground=self.colors["accent"]
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background=self.colors["background"],
            font=("Segoe UI", 11),
            foreground=self.colors["text_muted"]
        )
        
        style.configure("Card.TFrame", background=self.colors["card"], relief="flat", borderwidth=0)
        style.configure(
            "Card.TLabelframe",
            background=self.colors["card"],
            borderwidth=0,
            relief="flat"
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=self.colors["card"],
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["accent_dark"]
        )
        style.configure("QuestionContainer.TFrame", background=self.colors["card"])
        style.configure("QuestionBody.TFrame", background=self.colors["card"])
        style.configure("LabelCard.TLabel", background=self.colors["card"], font=("Segoe UI", 10, "bold"))
        style.configure("MutedCard.TLabel", background=self.colors["card"], foreground=self.colors["text_muted"])
        
        style.configure(
            "ScoreValue.TLabel",
            background=self.colors["card"],
            font=("Segoe UI", 20, "bold"),
            foreground=self.colors["accent"]
        )
        style.configure(
            "ScoreStatus.TLabel",
            background=self.colors["card"],
            font=("Segoe UI", 11, "bold"),
            foreground=self.colors["text_muted"]
        )
        style.configure(
            "Score.Horizontal.TProgressbar",
            troughcolor="#e2e8f0",
            bordercolor="#e2e8f0",
            background=self.colors["accent"],
            thickness=12
        )
        
        style.configure("Main.TEntry", padding=6, fieldbackground="#ffffff")
        style.configure("Main.TCombobox", padding=6, fieldbackground="#ffffff")
        style.configure("Main.TCheckbutton", background=self.colors["card"], foreground="#0f172a")
        
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.map(
            "Accent.TButton",
            background=[("disabled", "#94a3b8"), ("pressed", self.colors["accent_dark"]), ("active", self.colors["accent_dark"]), ("!disabled", self.colors["accent"])],
            foreground=[("disabled", "#e2e8f0"), ("!disabled", "#ffffff")]
        )
        style.configure("Secondary.TButton", padding=8, font=("Segoe UI", 10))
        style.map(
            "Secondary.TButton",
            background=[("pressed", "#cbd5f5"), ("active", "#dbeafe"), ("!disabled", "#e2e8f0")],
            foreground=[("disabled", "#94a3b8"), ("!disabled", "#0f172a")]
        )
        
        style.configure(
            "Question.TLabelframe",
            background=self.colors["card"],
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Question.TLabelframe.Label",
            background=self.colors["card"],
            font=("Segoe UI", 10, "bold"),
            foreground=self.colors["accent_dark"]
        )
        style.configure(
            "QuestionText.TLabel",
            background=self.colors["card"],
            font=("Segoe UI", 11),
            wraplength=900,
            foreground="#0f172a"
        )
        style.configure(
            "Question.TRadiobutton",
            background=self.colors["card"],
            font=("Segoe UI", 10),
            foreground="#0f172a"
        )
        style.map(
            "Question.TRadiobutton",
            foreground=[("selected", self.colors["accent_dark"]), ("active", self.colors["accent"])],
            background=[("active", self.colors["card"])]
        )
        style.configure(
            "Penalty.TLabel",
            background=self.colors["card"],
            font=("Segoe UI", 9, "italic"),
            foreground=self.colors["warning"]
        )
    
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Menú
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        admin_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Administración", menu=admin_menu)
        admin_menu.add_command(label="Áreas", command=self._open_area_admin)
        admin_menu.add_command(label="Casos", command=self._open_case_admin)
        admin_menu.add_command(label="Preguntas", command=self._open_question_admin)
        admin_menu.add_command(label="Perfiles", command=self._open_profile_admin)
        admin_menu.add_command(label="Tiers", command=self._open_tier_admin)
        
        # Menú de visualización
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Todas las Encuestas", command=self._open_surveys_view)
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20 20 20 15", style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Encabezado
        header_frame = ttk.Frame(main_frame, style="Header.TFrame", padding="0 5 0 10")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="Panel de Evaluación", style="HeaderTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header_frame,
            text="Gestiona los casos, aplica evaluaciones y monitorea el desempeño en un solo lugar.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W, pady=(2, 0))
        
        ttk.Separator(main_frame).pack(fill=tk.X, pady=(5, 15))
        
        # Frame superior - Información de evaluación
        top_frame = ttk.LabelFrame(main_frame, text="Información de Evaluación", padding="15", style="Card.TLabelframe")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        for col in range(4):
            top_frame.columnconfigure(col, weight=1)
        
        # Perfil del evaluador
        ttk.Label(top_frame, text="Perfil del Evaluador:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_combo = ttk.Combobox(top_frame, width=30, state="normal", style="Main.TCombobox")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.profile_combo.bind('<<ComboboxSelected>>', self._on_profile_changed)
        self.profile_combo.bind('<FocusIn>', lambda e: self.profile_combo.config(state='readonly'))
        
        # SID
        ttk.Label(top_frame, text="SID:", style="LabelCard.TLabel").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.sid_entry = ttk.Entry(top_frame, width=30, style="Main.TEntry")
        self.sid_entry.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        
        # Es graduado
        ttk.Label(top_frame, text="Es Graduado:", style="LabelCard.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.is_graduated_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_frame, text="Sí", variable=self.is_graduated_var, style="Main.TCheckbutton").grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Caso
        ttk.Label(top_frame, text="Caso:", style="LabelCard.TLabel").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.case_combo = ttk.Combobox(top_frame, width=30, state="normal", style="Main.TCombobox")
        self.case_combo.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)
        
        # Área
        ttk.Label(top_frame, text="Área:", style="LabelCard.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(top_frame, width=30, state="readonly", style="Main.TCombobox")
        self.area_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.area_combo.bind('<<ComboboxSelected>>', self._on_area_changed)
        
        # Botón cargar preguntas
        ttk.Button(top_frame, text="Cargar Preguntas", command=self._load_questions, style="Accent.TButton").grid(
            row=2, column=2, columnspan=2, padx=5, pady=5, sticky=tk.EW
        )
        
        ttk.Label(
            top_frame,
            text="Selecciona un perfil y un área para cargar automáticamente las preguntas disponibles.",
            style="MutedCard.TLabel"
        ).grid(row=3, column=0, columnspan=4, sticky=tk.W, padx=5, pady=(8, 0))
        
        # Puntaje actual
        score_frame = ttk.Frame(main_frame, style="Card.TFrame", padding="15 12")
        score_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(score_frame, text="Resumen del Puntaje", style="MutedCard.TLabel").pack(anchor=tk.W)
        self.score_label = ttk.Label(
            score_frame,
            text="Puntaje Actual: 100.0",
            style="ScoreValue.TLabel"
        )
        self.score_label.pack(anchor=tk.W)
        
        self.score_progress = ttk.Progressbar(
            score_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            style="Score.Horizontal.TProgressbar"
        )
        self.score_progress.pack(fill=tk.X, pady=6)
        
        self.score_status_label = ttk.Label(score_frame, style="ScoreStatus.TLabel")
        self.score_status_label.pack(anchor=tk.W, pady=(4, 0))
        self._update_score_visuals()
        
        self.tier_label = ttk.Label(
            score_frame,
            text="Tier Actual: Sin asignar",
            style="ScoreStatus.TLabel"
        )
        self.tier_label.pack(anchor=tk.W, pady=(6, 0))
        
        ttk.Separator(main_frame).pack(fill=tk.X, pady=(0, 15))
        
        # Frame de preguntas con scroll
        questions_frame = ttk.LabelFrame(main_frame, text="Preguntas", padding="10", style="Card.TLabelframe")
        questions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(questions_frame, highlightthickness=0, bg=self.colors["card"])
        scrollbar = ttk.Scrollbar(questions_frame, orient="vertical", command=canvas.yview)
        self.questions_container = ttk.Frame(canvas, style="QuestionContainer.TFrame")
        
        self.questions_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.questions_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame, style="Main.TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Guardar Evaluación", command=self._save_survey, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar CSV", command=self._export_csv, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar Excel", command=self._export_excel, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
    
    def _load_data(self):
        """Carga datos iniciales."""
        try:
            # Cargar perfiles
            profiles = self.profile_service.get_all_profiles(active_only=True)
            if profiles:
                profile_names = [p.name for p in profiles]
                self.profile_combo.config(state='normal')
                self.profile_combo['values'] = profile_names
                self.profile_combo.config(state='readonly')
                print(f"Perfiles cargados: {profile_names}")
            else:
                self.profile_combo.config(state='normal')
                self.profile_combo['values'] = []
                self.profile_combo.config(state='readonly')
            
            # Cargar áreas
            areas = self.area_service.get_all_areas(active_only=True)
            if areas:
                area_names = [a.name for a in areas]
                self.area_combo.config(state='normal')
                self.area_combo['values'] = area_names
                self.area_combo.config(state='readonly')
                print(f"Áreas cargadas: {area_names}")
            else:
                self.area_combo.config(state='normal')
                self.area_combo['values'] = []
                self.area_combo.config(state='readonly')
                messagebox.showwarning(
                    "Advertencia",
                    "No se encontraron áreas activas.\n\nVaya a Administración → Áreas para crear áreas."
                )
            
            # Los casos se cargarán cuando se seleccione un área
            self._update_cases_for_area()
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def _on_profile_changed(self, event=None):
        """Maneja el cambio de perfil."""
        if self.questions:
            # Recargar preguntas para aplicar prefills
            self._load_questions()
    
    def _on_area_changed(self, event=None):
        """Maneja el cambio de área seleccionada."""
        self._update_cases_for_area()
        self._update_tier_info(self.current_score)
    
    def _update_cases_for_area(self):
        """Actualiza la lista de casos según el área seleccionada."""
        area_name = self.area_combo.get()
        if area_name:
            areas = self.area_service.get_all_areas(active_only=False)
            area = next((a for a in areas if a.name == area_name), None)
            if area:
                cases = self.case_service.get_all_cases(active_only=True, area_id=area.id)
                case_names = [c.name for c in cases]
                self.case_combo.config(state='normal')
                self.case_combo['values'] = case_names
                print(f"Casos cargados para área {area_name}: {case_names}")
                self.selected_area_id = area.id
            else:
                self.case_combo.config(state='normal')
                self.case_combo['values'] = []
                self.selected_area_id = None
        else:
            self.case_combo.config(state='normal')
            self.case_combo['values'] = []
            self.selected_area_id = None
    
    def _load_questions(self):
        """Carga las preguntas activas."""
        if not self.profile_combo.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un perfil")
            return
        
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un área")
            return
        
        # Obtener perfil ID
        profile_name = self.profile_combo.get()
        profiles = self.profile_service.get_all_profiles(active_only=False)
        profile = next((p for p in profiles if p.name == profile_name), None)
        
        if not profile:
            messagebox.showerror("Error", "Perfil no encontrado")
            return
        
        profile_id = profile.id
        
        # Obtener área ID
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        area_id = area.id
        self.selected_area_id = area_id
        
        # Cargar preguntas activas del área seleccionada
        self.questions = self.question_service.get_all_questions(active_only=True, area_id=area_id)
        
        if not self.questions:
            messagebox.showinfo("Información", "No hay preguntas activas")
            return
        
        # Obtener prefills para este perfil
        defaults = self.question_service.get_defaults_for_profile(profile_id)
        
        # Renderizar preguntas
        self._render_questions(defaults)
        self._update_score()
    
    def _render_questions(self, defaults: Dict[int, str]):
        """Renderiza las preguntas en el panel."""
        # Limpiar contenedor
        for widget in self.questions_container.winfo_children():
            widget.destroy()
        
        self.current_responses = {}
        self.answer_vars = {}
        self.comment_entries = {}
        
        for question in self.questions:
            q_frame = ttk.LabelFrame(
                self.questions_container,
                text=f"Pregunta #{question.id}",
                padding="12",
                style="Question.TLabelframe"
            )
            q_frame.pack(fill=tk.X, pady=8, padx=5)
            
            # Texto de la pregunta
            ttk.Label(q_frame, text=question.text, style="QuestionText.TLabel", wraplength=900).pack(anchor=tk.W, pady=(0, 8))
            
            # Obtener respuesta por defecto
            default_answer = defaults.get(question.id, 'NA')
            
            # RadioButtons para respuestas
            answer_var = tk.StringVar(value=default_answer)
            self.answer_vars[question.id] = answer_var
            
            answer_frame = ttk.Frame(q_frame, style="QuestionBody.TFrame")
            answer_frame.pack(fill=tk.X, pady=5)
            
            ttk.Radiobutton(
                answer_frame,
                text="Sí",
                variable=answer_var,
                value="YES",
                style="Question.TRadiobutton",
                command=lambda qid=question.id: self._on_answer_change(qid)
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Radiobutton(
                answer_frame,
                text="No",
                variable=answer_var,
                value="NO",
                style="Question.TRadiobutton",
                command=lambda qid=question.id: self._on_answer_change(qid)
            ).pack(side=tk.LEFT, padx=10)
            
            ttk.Radiobutton(
                answer_frame,
                text="N/A",
                variable=answer_var,
                value="NA",
                style="Question.TRadiobutton",
                command=lambda qid=question.id: self._on_answer_change(qid)
            ).pack(side=tk.LEFT, padx=10)
            
            # Mostrar penalizaciones
            penalty_text = f"Penalización Graduado: {question.penalty_graduated} | No Graduado: {question.penalty_not_graduated}"
            ttk.Label(answer_frame, text=penalty_text, style="Penalty.TLabel").pack(side=tk.LEFT, padx=10)
            
            # Campo de comentario (visible solo si respuesta es NO)
            comment_frame = ttk.Frame(q_frame, style="QuestionBody.TFrame")
            comment_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(comment_frame, text="Comentario (obligatorio si No):", style="MutedCard.TLabel").pack(anchor=tk.W)
            comment_entry = tk.Text(comment_frame, height=3, width=80, wrap=tk.WORD)
            comment_entry.pack(fill=tk.X, pady=2)
            comment_entry.configure(
                bg="#f8fafc",
                relief="flat",
                font=("Segoe UI", 10),
                highlightthickness=1,
                highlightbackground=self.colors["border"],
                highlightcolor=self.colors["accent"],
                bd=0,
                padx=8,
                pady=6,
                insertbackground="#0f172a"
            )
            comment_entry.config(disabledbackground="#f8fafc", disabledforeground="#94a3b8")
            self.comment_entries[question.id] = comment_entry
            
            # Inicializar respuesta
            self._on_answer_change(question.id)
    
    def _on_answer_change(self, question_id: int):
        """Maneja el cambio de respuesta."""
        answer = self.answer_vars[question_id].get()
        comment_entry = self.comment_entries[question_id]
        
        # Mostrar/ocultar comentario según respuesta
        if answer == 'NO':
            comment_entry.config(state='normal')
        else:
            comment_entry.config(state='disabled')
            comment_entry.delete('1.0', tk.END)
        
        # Actualizar respuesta
        question = next((q for q in self.questions if q.id == question_id), None)
        if question:
            comment = comment_entry.get('1.0', tk.END).strip() if answer == 'NO' else None
            
            # Calcular penalización
            penalty = 0.0
            if answer == 'NO':
                penalty = question.get_penalty(self.is_graduated_var.get())
            
            self.current_responses[question_id] = SurveyResponse(
                id=None,
                survey_id=0,  # Temporal
                question_id=question_id,
                answer=answer,
                comment=comment,
                penalty_applied=penalty
            )
        
        self._update_score()
    
    def _update_score(self):
        """Actualiza el puntaje actual."""
        score = 100.0
        is_graduated = self.is_graduated_var.get()
        
        for question in self.questions:
            response = self.current_responses.get(question.id)
            if response and response.answer == 'NO':
                penalty = question.get_penalty(is_graduated)
                score -= penalty
        
        score = max(0.0, score)
        self.current_score = score
        self.score_label.config(text=f"Puntaje Actual: {score:.2f}")
        self._update_score_visuals()
    
    def _update_score_visuals(self):
        """Actualiza estilos del puntaje y el resumen visual."""
        if not hasattr(self, "score_progress"):
            return
        
        score = getattr(self, "current_score", 100.0)
        self.score_progress['value'] = score
        
        if score >= 80:
            status_text = "Estado: Excelente"
            color = self.colors["success"]
        elif score >= 60:
            status_text = "Estado: Atención"
            color = self.colors["warning"]
        else:
            status_text = "Estado: Crítico"
            color = self.colors["danger"]
        
        self.score_status_label.config(text=status_text, foreground=color)
        primary_color = self.colors["accent"] if score >= 60 else color
        self.score_label.config(foreground=primary_color)
        self._update_tier_info(score)
    
    def _update_tier_info(self, score: float):
        """Actualiza la visualización del tier actual."""
        if not hasattr(self, "tier_label"):
            return
        
        if not self.selected_area_id:
            self.current_tier = None
            self.tier_label.config(text="Tier Actual: Seleccione un área", foreground=self.colors["text_muted"])
            return
        
        tier = self.tier_service.get_tier_for_score(self.selected_area_id, score)
        self.current_tier = tier
        if tier:
            color = tier.color or self.colors["accent"]
            self.tier_label.config(
                text=f"Tier Actual: {tier.name} ({tier.min_score:.0f}-{tier.max_score:.0f})",
                foreground=color
            )
        else:
            self.tier_label.config(text="Tier Actual: No configurado", foreground=self.colors["danger"])
    
    def _save_survey(self):
        """Guarda la evaluación."""
        # Validaciones
        if not self.profile_combo.get():
            messagebox.showwarning("Advertencia", "Por favor seleccione un perfil")
            return
        
        if not self.sid_entry.get().strip():
            messagebox.showwarning("Advertencia", "Por favor ingrese el SID")
            return
        
        if not self.case_combo.get().strip():
            messagebox.showwarning("Advertencia", "Por favor ingrese o seleccione un caso")
            return
        
        if not self.questions:
            messagebox.showwarning("Advertencia", "Por favor cargue las preguntas")
            return
        
        # Validar comentarios obligatorios
        for question_id, response in self.current_responses.items():
            if response.answer == 'NO':
                comment_entry = self.comment_entries[question_id]
                comment = comment_entry.get('1.0', tk.END).strip()
                if not comment:
                    messagebox.showerror("Error", f"El comentario es obligatorio para la Pregunta #{question_id}")
                    return
                response.comment = comment
        
        try:
            # Obtener área
            area_name = self.area_combo.get()
            areas = self.area_service.get_all_areas(active_only=False)
            area = next((a for a in areas if a.name == area_name), None)
            if not area:
                messagebox.showerror("Error", "Área no encontrada")
                return
            
            # Obtener o crear caso
            case_name = self.case_combo.get().strip()
            case_id = self.case_service.find_or_create_case(area_id=area.id, name=case_name)
            
            # Crear respuestas finales
            responses = list(self.current_responses.values())
            
            survey_id = self.survey_service.create_survey(
                evaluator_profile=self.profile_combo.get(),
                sid=self.sid_entry.get().strip(),
                case_id=case_id,
                is_graduated=self.is_graduated_var.get(),
                responses=responses
            )
            
            tier_text = self.current_tier.name if self.current_tier else "No configurado"
            messagebox.showinfo(
                "Éxito",
                f"Evaluación guardada correctamente.\nPuntaje Final: {self.current_score:.2f}\nTier: {tier_text}"
            )
            
            # Limpiar formulario
            self.sid_entry.delete(0, tk.END)
            self.case_combo.set('')
            self.is_graduated_var.set(False)
            self.selected_area_id = None
            self.tier_label.config(text="Tier Actual: Sin asignar", foreground=self.colors["text_muted"])
            self.current_tier = None
            for widget in self.questions_container.winfo_children():
                widget.destroy()
            self.questions = []
            self.current_responses = {}
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def _export_csv(self):
        """Exporta las encuestas a CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filepath:
            if self.survey_service.export_to_csv(filepath):
                messagebox.showinfo("Éxito", f"Datos exportados a {filepath}")
            else:
                messagebox.showerror("Error", "Error al exportar datos")
    
    def _export_excel(self):
        """Exporta las encuestas a Excel."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filepath:
            if self.survey_service.export_to_excel(filepath):
                messagebox.showinfo("Éxito", f"Datos exportados a {filepath}")
            else:
                messagebox.showerror("Error", "Error al exportar datos. Asegúrese de tener openpyxl instalado.")
    
    def _open_area_admin(self):
        """Abre ventana de administración de áreas."""
        from src.ui.area_admin_window import AreaAdminWindow
        AreaAdminWindow(self.root, self.area_service)
    
    def _open_case_admin(self):
        """Abre ventana de administración de casos."""
        from src.ui.case_admin_window import CaseAdminWindow
        CaseAdminWindow(self.root, self.case_service, self.area_service)
    
    def _open_question_admin(self):
        """Abre ventana de administración de preguntas."""
        from src.ui.question_admin_window import QuestionAdminWindow
        QuestionAdminWindow(self.root, self.question_service, self.profile_service, self.area_service)
    
    def _open_profile_admin(self):
        """Abre ventana de administración de perfiles."""
        from src.ui.profile_admin_window import ProfileAdminWindow
        ProfileAdminWindow(self.root, self.profile_service)
    
    def _open_surveys_view(self):
        """Abre ventana de visualización de encuestas."""
        from src.ui.surveys_view_window import SurveysViewWindow
        SurveysViewWindow(self.root, self.survey_service, self.case_service, self.question_service)
    
    def _open_tier_admin(self):
        """Abre ventana de administración de tiers."""
        from src.ui.tier_admin_window import TierAdminWindow
        TierAdminWindow(self.root, self.tier_service, self.area_service)

