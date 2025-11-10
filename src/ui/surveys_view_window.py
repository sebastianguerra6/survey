"""Ventana para visualizar todas las encuestas y respuestas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import datetime
from src.services.survey_service import SurveyService
from src.services.case_service import CaseService
from src.services.question_service import QuestionService


class SurveysViewWindow:
    """Ventana para ver todas las encuestas y sus respuestas."""
    
    def __init__(self, parent, survey_service: SurveyService, case_service: CaseService, question_service: QuestionService):
        """Inicializa la ventana."""
        self.survey_service = survey_service
        self.case_service = case_service
        self.question_service = question_service
        
        self.window = tk.Toplevel(parent)
        self.window.title("Visualizar Encuestas y Respuestas")
        self.window.geometry("1200x700")
        
        self.selected_survey_id: Optional[int] = None
        
        self._setup_ui()
        self._load_surveys()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame principal con paneles divididos
        main_paned = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo: Lista de encuestas
        left_frame = ttk.LabelFrame(main_paned, text="Encuestas", padding="10")
        main_paned.add(left_frame, weight=1)
        
        # Tabla de encuestas
        columns = ('ID', 'Fecha', 'Perfil', 'SID', 'Caso', 'Graduado', 'Puntaje')
        self.surveys_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        self.surveys_tree.heading('ID', text='ID')
        self.surveys_tree.heading('Fecha', text='Fecha')
        self.surveys_tree.heading('Perfil', text='Perfil Evaluador')
        self.surveys_tree.heading('SID', text='SID')
        self.surveys_tree.heading('Caso', text='Caso')
        self.surveys_tree.heading('Graduado', text='Graduado')
        self.surveys_tree.heading('Puntaje', text='Puntaje')
        
        self.surveys_tree.column('ID', width=50)
        self.surveys_tree.column('Fecha', width=150)
        self.surveys_tree.column('Perfil', width=120)
        self.surveys_tree.column('SID', width=100)
        self.surveys_tree.column('Caso', width=150)
        self.surveys_tree.column('Graduado', width=80)
        self.surveys_tree.column('Puntaje', width=80)
        
        scrollbar_surveys = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.surveys_tree.yview)
        self.surveys_tree.configure(yscrollcommand=scrollbar_surveys.set)
        
        self.surveys_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_surveys.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.surveys_tree.bind('<<TreeviewSelect>>', self._on_survey_select)
        
        # Panel derecho: Detalles y respuestas
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        # Frame de información de la encuesta
        info_frame = ttk.LabelFrame(right_frame, text="Información de la Encuesta", padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame de respuestas
        responses_frame = ttk.LabelFrame(right_frame, text="Respuestas Detalladas", padding="10")
        responses_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabla de respuestas
        response_columns = ('Pregunta', 'Respuesta', 'Comentario', 'Penalización')
        self.responses_tree = ttk.Treeview(responses_frame, columns=response_columns, show='headings', height=15)
        
        self.responses_tree.heading('Pregunta', text='Pregunta')
        self.responses_tree.heading('Respuesta', text='Respuesta')
        self.responses_tree.heading('Comentario', text='Comentario')
        self.responses_tree.heading('Penalización', text='Penalización')
        
        self.responses_tree.column('Pregunta', width=400)
        self.responses_tree.column('Respuesta', width=100)
        self.responses_tree.column('Comentario', width=300)
        self.responses_tree.column('Penalización', width=100)
        
        scrollbar_responses = ttk.Scrollbar(responses_frame, orient=tk.VERTICAL, command=self.responses_tree.yview)
        self.responses_tree.configure(yscrollcommand=scrollbar_responses.set)
        
        self.responses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_responses.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Actualizar", command=self._load_surveys).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_surveys(self):
        """Carga todas las encuestas en la tabla."""
        # Limpiar tabla
        for item in self.surveys_tree.get_children():
            self.surveys_tree.delete(item)
        
        try:
            surveys = self.survey_service.get_all_surveys()
            
            # Obtener nombres de casos
            cases = {c.id: c.name for c in self.case_service.get_all_cases(active_only=False)}
            
            # Configurar tags para colorear según puntaje
            self.surveys_tree.tag_configure('low_score', background='#ffcccc')  # Rojo claro para < 60
            self.surveys_tree.tag_configure('medium_score', background='#ffffcc')  # Amarillo claro para 60-79
            self.surveys_tree.tag_configure('high_score', background='#ccffcc')  # Verde claro para >= 80
            
            for survey in surveys:
                case_name = cases.get(survey.case_id, 'N/A')
                fecha_str = survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else 'N/A'
                graduado_str = 'Sí' if survey.is_graduated else 'No'
                
                # Determinar tag según puntaje
                if survey.final_score < 60:
                    tag = 'low_score'
                elif survey.final_score < 80:
                    tag = 'medium_score'
                else:
                    tag = 'high_score'
                
                self.surveys_tree.insert('', tk.END, values=(
                    survey.id,
                    fecha_str,
                    survey.evaluator_profile,
                    survey.sid,
                    case_name,
                    graduado_str,
                    f"{survey.final_score:.2f}"
                ), tags=(tag,))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar encuestas: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _on_survey_select(self, event):
        """Maneja la selección de una encuesta."""
        selection = self.surveys_tree.selection()
        if not selection:
            return
        
        item = self.surveys_tree.item(selection[0])
        survey_id = item['values'][0]
        self.selected_survey_id = survey_id
        
        try:
            survey = self.survey_service.get_survey(survey_id)
            if not survey:
                messagebox.showerror("Error", "Encuesta no encontrada")
                return
            
            # Mostrar información de la encuesta
            self._show_survey_info(survey)
            
            # Mostrar respuestas
            self._show_responses(survey)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _show_survey_info(self, survey):
        """Muestra la información de la encuesta seleccionada."""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete('1.0', tk.END)
        
        case = self.case_service.get_case(survey.case_id)
        case_name = case.name if case else 'N/A'
        
        fecha_str = survey.created_at.strftime('%Y-%m-%d %H:%M:%S') if survey.created_at else 'N/A'
        
        info = f"""ID de Encuesta: {survey.id}
Perfil del Evaluador: {survey.evaluator_profile}
SID: {survey.sid}
Caso: {case_name}
Es Graduado: {'Sí' if survey.is_graduated else 'No'}
Puntaje Final: {survey.final_score:.2f} / 100.00
Fecha de Creación: {fecha_str}
Total de Respuestas: {len(survey.responses)}
"""
        
        self.info_text.insert('1.0', info)
        self.info_text.config(state=tk.DISABLED)
    
    def _show_responses(self, survey):
        """Muestra las respuestas de la encuesta seleccionada."""
        # Limpiar tabla
        for item in self.responses_tree.get_children():
            self.responses_tree.delete(item)
        
        try:
            # Obtener todas las preguntas para mostrar el texto
            questions = self.question_service.get_all_questions(active_only=False)
            questions_map = {q.id: q for q in questions}
            
            for response in survey.responses:
                question = questions_map.get(response.question_id)
                question_text = question.text if question else f"Pregunta ID: {response.question_id}"
                
                # Truncar texto largo
                if len(question_text) > 80:
                    question_text = question_text[:77] + '...'
                
                # Mapear respuestas
                answer_map = {'YES': 'Sí', 'NO': 'No', 'NA': 'N/A'}
                answer_str = answer_map.get(response.answer, response.answer)
                
                # Comentario
                comment = response.comment or ''
                if len(comment) > 60:
                    comment = comment[:57] + '...'
                
                # Penalización
                penalty_str = f"{response.penalty_applied:.2f}" if response.penalty_applied > 0 else "0.00"
                
                self.responses_tree.insert('', tk.END, values=(
                    question_text,
                    answer_str,
                    comment,
                    penalty_str
                ))
                
                # Colorear filas según respuesta
                if response.answer == 'NO':
                    item_id = self.responses_tree.get_children()[-1]
                    self.responses_tree.set(item_id, 'Respuesta', answer_str)
                    # Configurar color para respuestas NO
                    self.responses_tree.item(item_id, tags=('no_answer',))
                    self.responses_tree.tag_configure('no_answer', background='#ffe6e6')
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar respuestas: {str(e)}")
            import traceback
            traceback.print_exc()

