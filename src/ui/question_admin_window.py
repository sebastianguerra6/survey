"""Ventana de administración de Preguntas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional
from src.services.question_service import QuestionService
from src.services.profile_service import ProfileService
from src.services.area_service import AreaService


class QuestionAdminWindow(ttk.Frame):
    """Vista incrustada para administrar preguntas y prefills."""
    
    def __init__(
        self,
        parent,
        question_service: QuestionService,
        profile_service: ProfileService,
        area_service: AreaService,
        colors: Dict[str, str],
        on_back: Callable[[], None],
    ):
        super().__init__(parent, padding="20 20 20 15", style="Main.TFrame")
        self.question_service = question_service
        self.profile_service = profile_service
        self.area_service = area_service
        self.colors = colors
        self.on_back = on_back
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_questions()
        self._load_profiles()
        self._load_areas()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(header, text="< Volver al Panel", command=self.on_back, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Label(header, text="Administración de Preguntas", style="HeaderTitle.TLabel").pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            header,
            text="Gestiona el banco de preguntas, sus penalizaciones y respuestas por defecto.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W)
        
        form_frame = ttk.LabelFrame(self, text="Nuevo/Editar Pregunta", padding="15", style="Card.TLabelframe")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(2, weight=1)
        
        ttk.Label(form_frame, text="Área:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(form_frame, state="readonly", style="Main.TCombobox")
        self.area_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activa", variable=self.active_var, style="Main.TCheckbutton").grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.W
        )
        
        ttk.Label(form_frame, text="Texto:", style="LabelCard.TLabel").grid(row=1, column=0, sticky=tk.NW, padx=5, pady=5)
        self.text_entry = tk.Text(form_frame, height=4, wrap=tk.WORD)
        self.text_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        self.text_entry.configure(
            bg="#f8fafc",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            font=("Segoe UI", 10),
            padx=8,
            pady=6
        )
        
        ttk.Label(form_frame, text="Penalización Graduado:", style="LabelCard.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.penalty_graduated_entry = ttk.Entry(form_frame, style="Main.TEntry")
        self.penalty_graduated_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.penalty_graduated_entry.insert(0, "0.0")
        
        ttk.Label(form_frame, text="Penalización No Graduado:", style="LabelCard.TLabel").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.penalty_not_graduated_entry = ttk.Entry(form_frame, style="Main.TEntry")
        self.penalty_not_graduated_entry.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        self.penalty_not_graduated_entry.insert(0, "0.0")
        
        button_frame = ttk.Frame(form_frame, style="Main.TFrame")
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        prefills_frame = ttk.LabelFrame(self, text="Respuestas por Defecto por Perfil", padding="15", style="Card.TLabelframe")
        prefills_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        prefills_frame.columnconfigure(1, weight=1)
        prefills_frame.columnconfigure(3, weight=1)
        
        ttk.Label(prefills_frame, text="Perfil:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_combo = ttk.Combobox(prefills_frame, state="readonly", style="Main.TCombobox")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(prefills_frame, text="Respuesta por Defecto:", style="LabelCard.TLabel").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.default_answer_combo = ttk.Combobox(
            prefills_frame,
            values=["YES", "NO", "NA"],
            state="readonly",
            style="Main.TCombobox"
        )
        self.default_answer_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Button(prefills_frame, text="Guardar Prefill", command=self._save_prefill, style="Accent.TButton").grid(
            row=0, column=4, padx=5, pady=5
        )
        
        ttk.Label(prefills_frame, text="Prefills Configurados:", style="MutedCard.TLabel").grid(
            row=1, column=0, columnspan=5, sticky=tk.W, padx=5, pady=(10, 5)
        )
        
        self.prefills_tree = ttk.Treeview(prefills_frame, columns=('Perfil', 'Respuesta'), show='headings', height=8)
        self.prefills_tree.heading('Perfil', text='Perfil')
        self.prefills_tree.heading('Respuesta', text='Respuesta')
        self.prefills_tree.column('Perfil', width=220)
        self.prefills_tree.column('Respuesta', width=150)
        self.prefills_tree.grid(row=2, column=0, columnspan=5, sticky=tk.NSEW, padx=5, pady=5)
        prefills_frame.rowconfigure(2, weight=1)
        
        list_frame = ttk.LabelFrame(self, text="Preguntas Existentes", padding="15", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Área', 'Texto', 'Penalización Grad', 'Penalización No Grad', 'Activa')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            width = 80 if col == 'ID' else 150
            if col == 'Texto':
                width = 280
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        action_frame = ttk.Frame(list_frame, style="Main.TFrame")
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Editar", command=self._edit, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._delete, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
    
    def _load_profiles(self):
        """Carga los perfiles."""
        profiles = self.profile_service.get_all_profiles(active_only=False)
        profile_names = [p.name for p in profiles]
        self.profile_combo['values'] = profile_names
    
    def _load_areas(self):
        """Carga las áreas."""
        areas = self.area_service.get_all_areas(active_only=False)
        area_names = [a.name for a in areas]
        self.area_combo['values'] = area_names
    
    def _load_questions(self):
        """Carga las preguntas en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        questions = self.question_service.get_all_questions(active_only=False)
        areas = {a.id: a.name for a in self.area_service.get_all_areas(active_only=False)}
        
        for question in questions:
            text_short = question.text[:50] + '...' if len(question.text) > 50 else question.text
            area_name = areas.get(question.area_id, 'N/A')
            self.tree.insert('', tk.END, values=(
                question.id,
                area_name,
                text_short,
                question.penalty_graduated,
                question.penalty_not_graduated,
                'Sí' if question.active else 'No'
            ))
    
    def _load_prefills(self):
        """Carga los prefills para la pregunta seleccionada."""
        if not self.selected_id:
            return
        
        # Limpiar tree
        for item in self.prefills_tree.get_children():
            self.prefills_tree.delete(item)
        
        # Obtener perfiles
        profiles = self.profile_service.get_all_profiles(active_only=False)
        
        # Obtener prefills para esta pregunta
        for profile in profiles:
            defaults = self.question_service.get_defaults_for_profile(profile.id)
            if self.selected_id in defaults:
                self.prefills_tree.insert('', tk.END, values=(
                    profile.name,
                    defaults[self.selected_id]
                ))
    
    def _on_select(self, event):
        """Maneja la selección de una pregunta."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            question = self.question_service.get_question(self.selected_id)
            if question:
                # Cargar área
                areas = self.area_service.get_all_areas(active_only=False)
                area = next((a for a in areas if a.id == question.area_id), None)
                if area:
                    self.area_combo.set(area.name)
                
                self.text_entry.delete('1.0', tk.END)
                self.text_entry.insert('1.0', question.text)
                self.penalty_graduated_entry.delete(0, tk.END)
                self.penalty_graduated_entry.insert(0, str(question.penalty_graduated))
                self.penalty_not_graduated_entry.delete(0, tk.END)
                self.penalty_not_graduated_entry.insert(0, str(question.penalty_not_graduated))
                self.active_var.set(question.active)
                self._load_prefills()
    
    def _create(self):
        """Crea una nueva pregunta."""
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El área es obligatoria")
            return
        
        text = self.text_entry.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Advertencia", "El texto es obligatorio")
            return
        
        # Obtener área ID
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        try:
            penalty_graduated = float(self.penalty_graduated_entry.get())
            penalty_not_graduated = float(self.penalty_not_graduated_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Las penalizaciones deben ser números")
            return
        
        try:
            self.question_service.create_question(
                area_id=area.id,
                text=text,
                penalty_graduated=penalty_graduated,
                penalty_not_graduated=penalty_not_graduated,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Pregunta creada correctamente")
            self._clear_form()
            self._load_questions()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear: {str(e)}")
    
    def _update(self):
        """Actualiza una pregunta."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione una pregunta para editar")
            return
        
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El área es obligatoria")
            return
        
        text = self.text_entry.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Advertencia", "El texto es obligatorio")
            return
        
        # Obtener área ID
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        try:
            penalty_graduated = float(self.penalty_graduated_entry.get())
            penalty_not_graduated = float(self.penalty_not_graduated_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Las penalizaciones deben ser números")
            return
        
        try:
            self.question_service.update_question(
                question_id=self.selected_id,
                area_id=area.id,
                text=text,
                penalty_graduated=penalty_graduated,
                penalty_not_graduated=penalty_not_graduated,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Pregunta actualizada correctamente")
            self._clear_form()
            self._load_questions()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _delete(self):
        """Elimina una pregunta."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione una pregunta para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta pregunta?"):
            try:
                self.question_service.delete_question(self.selected_id)
                messagebox.showinfo("Éxito", "Pregunta eliminada correctamente")
                self._clear_form()
                self._load_questions()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def _save_prefill(self):
        """Guarda un prefill."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione una pregunta primero")
            return
        
        if not self.profile_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione un perfil")
            return
        
        if not self.default_answer_combo.get():
            messagebox.showwarning("Advertencia", "Seleccione una respuesta por defecto")
            return
        
        profile_name = self.profile_combo.get()
        profiles = self.profile_service.get_all_profiles(active_only=False)
        profile = next((p for p in profiles if p.name == profile_name), None)
        
        if not profile:
            messagebox.showerror("Error", "Perfil no encontrado")
            return
        
        try:
            self.question_service.set_default_answer(
                profile_id=profile.id,
                question_id=self.selected_id,
                default_answer=self.default_answer_combo.get()
            )
            messagebox.showinfo("Éxito", "Prefill guardado correctamente")
            self._load_prefills()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar prefill: {str(e)}")
    
    def _edit(self):
        """Habilita edición del elemento seleccionado."""
        self._on_select(None)
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.area_combo.set('')
        self.text_entry.delete('1.0', tk.END)
        self.penalty_graduated_entry.delete(0, tk.END)
        self.penalty_graduated_entry.insert(0, "0.0")
        self.penalty_not_graduated_entry.delete(0, tk.END)
        self.penalty_not_graduated_entry.insert(0, "0.0")
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        self._load_prefills()

