"""Ventana de administración de Preguntas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.services.question_service import QuestionService
from src.services.profile_service import ProfileService


class QuestionAdminWindow:
    """Ventana para CRUD de preguntas."""
    
    def __init__(self, parent, question_service: QuestionService, profile_service: ProfileService):
        """Inicializa la ventana."""
        self.question_service = question_service
        self.profile_service = profile_service
        
        self.window = tk.Toplevel(parent)
        self.window.title("Administración de Preguntas")
        self.window.geometry("900x700")
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_questions()
        self._load_profiles()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame de formulario
        form_frame = ttk.LabelFrame(self.window, text="Nuevo/Editar Pregunta", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Texto
        ttk.Label(form_frame, text="Texto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.text_entry = tk.Text(form_frame, width=60, height=3)
        self.text_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)
        
        # Penalización Graduado
        ttk.Label(form_frame, text="Penalización Graduado:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.penalty_graduated_entry = ttk.Entry(form_frame, width=20)
        self.penalty_graduated_entry.grid(row=1, column=1, padx=5, pady=5)
        self.penalty_graduated_entry.insert(0, "0.0")
        
        # Penalización No Graduado
        ttk.Label(form_frame, text="Penalización No Graduado:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.penalty_not_graduated_entry = ttk.Entry(form_frame, width=20)
        self.penalty_not_graduated_entry.grid(row=1, column=3, padx=5, pady=5)
        self.penalty_not_graduated_entry.insert(0, "0.0")
        
        # Activa
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activa", variable=self.active_var).grid(
            row=2, column=0, padx=5, pady=5
        )
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Frame de prefills por perfil
        prefills_frame = ttk.LabelFrame(self.window, text="Respuestas por Defecto por Perfil", padding="10")
        prefills_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Perfil selector
        ttk.Label(prefills_frame, text="Perfil:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.profile_combo = ttk.Combobox(prefills_frame, width=30, state="readonly")
        self.profile_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Respuesta por defecto
        ttk.Label(prefills_frame, text="Respuesta por Defecto:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.default_answer_combo = ttk.Combobox(
            prefills_frame,
            values=["YES", "NO", "NA"],
            width=15,
            state="readonly"
        )
        self.default_answer_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(prefills_frame, text="Guardar Prefill", command=self._save_prefill).grid(
            row=0, column=4, padx=5, pady=5
        )
        
        # Lista de prefills
        ttk.Label(prefills_frame, text="Prefills Configurados:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.prefills_tree = ttk.Treeview(prefills_frame, columns=('Perfil', 'Respuesta'), show='headings', height=10)
        self.prefills_tree.heading('Perfil', text='Perfil')
        self.prefills_tree.heading('Respuesta', text='Respuesta')
        self.prefills_tree.column('Perfil', width=200)
        self.prefills_tree.column('Respuesta', width=150)
        self.prefills_tree.grid(row=2, column=0, columnspan=5, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        # Lista de preguntas
        list_frame = ttk.LabelFrame(self.window, text="Preguntas Existentes", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Texto', 'Penalización Grad', 'Penalización No Grad', 'Activa')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Botones de acción
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(action_frame, text="Editar", command=self._edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._delete).pack(side=tk.LEFT, padx=5)
    
    def _load_profiles(self):
        """Carga los perfiles."""
        profiles = self.profile_service.get_all_profiles(active_only=False)
        profile_names = [p.name for p in profiles]
        self.profile_combo['values'] = profile_names
    
    def _load_questions(self):
        """Carga las preguntas en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        questions = self.question_service.get_all_questions(active_only=False)
        
        for question in questions:
            text_short = question.text[:50] + '...' if len(question.text) > 50 else question.text
            self.tree.insert('', tk.END, values=(
                question.id,
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
        text = self.text_entry.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Advertencia", "El texto es obligatorio")
            return
        
        try:
            penalty_graduated = float(self.penalty_graduated_entry.get())
            penalty_not_graduated = float(self.penalty_not_graduated_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Las penalizaciones deben ser números")
            return
        
        try:
            self.question_service.create_question(
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
        
        text = self.text_entry.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Advertencia", "El texto es obligatorio")
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
        self.text_entry.delete('1.0', tk.END)
        self.penalty_graduated_entry.delete(0, tk.END)
        self.penalty_graduated_entry.insert(0, "0.0")
        self.penalty_not_graduated_entry.delete(0, tk.END)
        self.penalty_not_graduated_entry.insert(0, "0.0")
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
        self._load_prefills()

