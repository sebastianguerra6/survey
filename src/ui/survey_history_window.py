"""Ventana para visualizar el historial de respuestas de un SID."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, List
from src.services.survey_service import SurveyService
from src.services.case_service import CaseService
from src.services.question_service import QuestionService
from src.models.survey import Survey


class SurveyHistoryWindow(tk.Toplevel):
    """Ventana modal que muestra el histórico de encuestas de un SID."""

    def __init__(
        self,
        parent: tk.Tk,
        sid: str,
        survey_service: SurveyService,
        case_service: CaseService,
        question_service: QuestionService,
        colors: Dict[str, str],
    ):
        super().__init__(parent)
        self.title(f"Historial de Evaluaciones - SID {sid}")
        self.geometry("1100x650")
        self.configure(bg=colors["background"])
        self.sid = sid
        self.survey_service = survey_service
        self.case_service = case_service
        self.question_service = question_service
        self.colors = colors
        self.history: List[Survey] = []
        self.selected_survey: Optional[Survey] = None
        self.questions_map = {
            q.id: q for q in self.question_service.get_all_questions(active_only=False)
        }

        self._build_ui()
        self._load_history()

    def _build_ui(self):
        """Crea los widgets principales."""
        header = ttk.Frame(self, style="Header.TFrame", padding="15 15 15 5")
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text=f"Historial de Respuestas para SID {self.sid}",
            style="HeaderTitle.TLabel",
        ).pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Consulta cada evaluación previa, su puntaje final y el tier asignado.",
            style="HeaderSubtitle.TLabel",
        ).pack(anchor=tk.W, pady=(2, 5))

        ttk.Button(
            header, text="Cerrar", command=self.destroy, style="Secondary.TButton"
        ).pack(side=tk.RIGHT)

        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Panel izquierdo con la tabla de encuestas históricas
        left_frame = ttk.LabelFrame(
            main_paned,
            text="Evaluaciones Registradas",
            padding="12",
            style="Card.TLabelframe",
        )
        main_paned.add(left_frame, weight=1)

        columns = ("ID", "Fecha", "Caso", "Perfil", "Graduado", "Puntaje", "Tier")
        self.history_tree = ttk.Treeview(
            left_frame, columns=columns, show="headings", height=20
        )

        for col, width in zip(
            columns, [60, 150, 160, 120, 80, 80, 120]
        ):
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=width, anchor=tk.CENTER)

        history_scroll = ttk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.bind("<<TreeviewSelect>>", self._on_history_select)

        # Panel derecho con detalles y respuestas
        right_frame = ttk.Frame(main_paned, style="Main.TFrame")
        main_paned.add(right_frame, weight=2)

        summary_frame = ttk.LabelFrame(
            right_frame, text="Resumen de la Evaluación", padding="12", style="Card.TLabelframe"
        )
        summary_frame.pack(fill=tk.X, pady=5)

        self.summary_label = ttk.Label(
            summary_frame,
            text="Selecciona una evaluación para ver el detalle.",
            style="MutedCard.TLabel",
        )
        self.summary_label.pack(anchor=tk.W)

        responses_frame = ttk.LabelFrame(
            right_frame, text="Respuestas Registradas", padding="12", style="Card.TLabelframe"
        )
        responses_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        response_columns = ("Pregunta", "Respuesta", "Comentario", "Penalización")
        self.responses_tree = ttk.Treeview(
            responses_frame, columns=response_columns, show="headings", height=18
        )

        self.responses_tree.heading("Pregunta", text="Pregunta")
        self.responses_tree.column("Pregunta", width=420, anchor=tk.W)
        self.responses_tree.heading("Respuesta", text="Respuesta")
        self.responses_tree.column("Respuesta", width=100, anchor=tk.CENTER)
        self.responses_tree.heading("Comentario", text="Comentario")
        self.responses_tree.column("Comentario", width=260, anchor=tk.W)
        self.responses_tree.heading("Penalización", text="Penalización")
        self.responses_tree.column("Penalización", width=120, anchor=tk.CENTER)

        responses_scroll = ttk.Scrollbar(
            responses_frame, orient=tk.VERTICAL, command=self.responses_tree.yview
        )
        self.responses_tree.configure(yscrollcommand=responses_scroll.set)
        self.responses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        responses_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _load_history(self):
        """Carga las evaluaciones del SID."""
        try:
            self.history = self.survey_service.get_history_for_sid(self.sid)
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            if not self.history:
                messagebox.showinfo(
                    "Sin registros",
                    f"No se encontraron evaluaciones previas para el SID {self.sid}.",
                )
                return

            cases = {c.id: c.name for c in self.case_service.get_all_cases(active_only=False)}

            for survey in self.history:
                fecha = (
                    survey.created_at.strftime("%Y-%m-%d %H:%M")
                    if survey.created_at
                    else "N/A"
                )
                case_name = cases.get(survey.case_id, "N/A")
                graduado = "Sí" if survey.is_graduated else "No"
                tier = survey.tier_name or "Sin tier"
                tag = self._get_score_tag(survey.final_score)

                self.history_tree.insert(
                    "",
                    tk.END,
                    values=(
                        survey.id,
                        fecha,
                        case_name,
                        survey.evaluator_profile,
                        graduado,
                        f"{survey.final_score:.2f}",
                        tier,
                    ),
                    tags=(tag,),
                )

            self.history_tree.tag_configure("low_score", background="#ffe2e5")
            self.history_tree.tag_configure("medium_score", background="#fff6db")
            self.history_tree.tag_configure("high_score", background="#e4ffe1")

        except Exception as exc:
            messagebox.showerror(
                "Error",
                f"Ocurrió un error al cargar el historial para SID {self.sid}.\n\n{exc}",
            )

    @staticmethod
    def _get_score_tag(score: float) -> str:
        """Devuelve un tag de color según el puntaje."""
        if score < 60:
            return "low_score"
        if score < 80:
            return "medium_score"
        return "high_score"

    def _on_history_select(self, _event):
        """Muestra los detalles de la evaluación seleccionada."""
        selection = self.history_tree.selection()
        if not selection:
            return

        item = self.history_tree.item(selection[0])
        survey_id = item["values"][0]
        survey = next((s for s in self.history if s.id == survey_id), None)
        if not survey:
            return

        self.selected_survey = survey
        self._update_summary(survey)
        self._populate_responses(survey)

    def _update_summary(self, survey: Survey):
        """Actualiza el resumen superior."""
        fecha = survey.created_at.strftime("%Y-%m-%d %H:%M") if survey.created_at else "N/A"
        tier_label = survey.tier_name or "Sin tier configurado"
        self.summary_label.config(
            text=(
                f"Encuesta #{survey.id} - Fecha: {fecha}\n"
                f"Puntaje Final: {survey.final_score:.2f} / 100.00\n"
                f"Tier asignado: {tier_label}"
            ),
            foreground=self.colors["accent_dark"],
        )

    def _populate_responses(self, survey: Survey):
        """Llena la tabla con las respuestas de la encuesta."""
        for item in self.responses_tree.get_children():
            self.responses_tree.delete(item)

        answer_map = {"YES": "Sí", "NO": "No", "NA": "N/A"}
        for response in survey.responses:
            question = self.questions_map.get(response.question_id)
            question_text = question.text if question else f"Pregunta ID {response.question_id}"
            if len(question_text) > 90:
                question_text = question_text[:87] + "..."

            comment = response.comment or ""
            if len(comment) > 80:
                comment = comment[:77] + "..."

            penalty = f"{response.penalty_applied:.2f}"

            item_id = self.responses_tree.insert(
                "",
                tk.END,
                values=(
                    question_text,
                    answer_map.get(response.answer, response.answer),
                    comment,
                    penalty,
                ),
            )

            if response.answer == "NO":
                self.responses_tree.item(item_id, tags=("no_answer",))

        self.responses_tree.tag_configure("no_answer", background="#ffecec")


