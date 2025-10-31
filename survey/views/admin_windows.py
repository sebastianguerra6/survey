"""Ventanas de administración."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from ..controllers.admin_controller import AdminController


class CaseAdminWindow:
    """Ventana de administración de Casos."""
    
    def __init__(self, parent, controller: AdminController, callback: Optional[Callable] = None):
        """Inicializa la ventana."""
        self.controller = controller
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Administración de Casos")
        self.window.geometry("600x400")
        
        self._setup_ui()
        self._load_cases()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame de formulario
        form_frame = ttk.LabelFrame(self.window, text="Nuevo/Editar Caso", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var).grid(row=0, column=2, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        self.selected_id: Optional[int] = None
        
        # Lista de casos
        list_frame = ttk.LabelFrame(self.window, text="Casos Existentes", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Nombre', 'Activo')
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
    
    def _load_cases(self):
        """Carga los casos en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cases = self.controller.get_all_cases(active_only=False)
        for case in cases:
            self.tree.insert('', tk.END, values=(case.id, case.name, 'Sí' if case.active else 'No'))
    
    def _on_select(self, event):
        """Maneja la selección de un caso."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            case = self.controller.get_case(self.selected_id)
            if case:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, case.name)
                self.active_var.set(case.active)
    
    def _create(self):
        """Crea un nuevo caso."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.controller.create_case(name, self.active_var.get())
            messagebox.showinfo("Éxito", "Caso creado correctamente")
            self._clear_form()
            self._load_cases()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear caso: {str(e)}")
    
    def _update(self):
        """Actualiza un caso."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un caso para editar")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.controller.update_case(self.selected_id, name, self.active_var.get())
            messagebox.showinfo("Éxito", "Caso actualizado correctamente")
            self._clear_form()
            self._load_cases()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar caso: {str(e)}")
    
    def _delete(self):
        """Elimina un caso."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un caso para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este caso?"):
            try:
                self.controller.delete_case(self.selected_id)
                messagebox.showinfo("Éxito", "Caso eliminado correctamente")
                self._clear_form()
                self._load_cases()
                if self.callback:
                    self.callback()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar caso: {str(e)}")
    
    def _edit(self):
        """Habilita edición del caso seleccionado."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un caso para editar")
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.name_entry.delete(0, tk.END)
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())


class AreaAdminWindow:
    """Ventana de administración de Áreas."""
    
    def __init__(self, parent, controller: AdminController, callback: Optional[Callable] = None):
        """Inicializa la ventana."""
        self.controller = controller
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Administración de Áreas")
        self.window.geometry("600x400")
        
        self._setup_ui()
        self._load_areas()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame de formulario
        form_frame = ttk.LabelFrame(self.window, text="Nuevo/Editar Área", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var).grid(row=0, column=2, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        self.selected_id: Optional[int] = None
        
        # Lista de áreas
        list_frame = ttk.LabelFrame(self.window, text="Áreas Existentes", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Nombre', 'Activo')
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
    
    def _load_areas(self):
        """Carga las áreas en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        areas = self.controller.get_all_areas(active_only=False)
        for area in areas:
            self.tree.insert('', tk.END, values=(area.id, area.name, 'Sí' if area.active else 'No'))
    
    def _on_select(self, event):
        """Maneja la selección de un área."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            area = self.controller.get_area(self.selected_id)
            if area:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, area.name)
                self.active_var.set(area.active)
    
    def _create(self):
        """Crea una nueva área."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.controller.create_area(name, self.active_var.get())
            messagebox.showinfo("Éxito", "Área creada correctamente")
            self._clear_form()
            self._load_areas()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear área: {str(e)}")
    
    def _update(self):
        """Actualiza un área."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un área para editar")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.controller.update_area(self.selected_id, name, self.active_var.get())
            messagebox.showinfo("Éxito", "Área actualizada correctamente")
            self._clear_form()
            self._load_areas()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar área: {str(e)}")
    
    def _delete(self):
        """Elimina un área."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un área para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta área?"):
            try:
                self.controller.delete_area(self.selected_id)
                messagebox.showinfo("Éxito", "Área eliminada correctamente")
                self._clear_form()
                self._load_areas()
                if self.callback:
                    self.callback()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar área: {str(e)}")
    
    def _edit(self):
        """Habilita edición del área seleccionada."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un área para editar")
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.name_entry.delete(0, tk.END)
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())


class QuestionAdminWindow:
    """Ventana de administración de Preguntas."""
    
    def __init__(self, parent, controller: AdminController):
        """Inicializa la ventana."""
        self.controller = controller
        
        self.window = tk.Toplevel(parent)
        self.window.title("Administración de Preguntas")
        self.window.geometry("900x600")
        
        self._setup_ui()
        self._load_questions()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame de formulario
        form_frame = ttk.LabelFrame(self.window, text="Nuevo/Editar Pregunta", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Área
        ttk.Label(form_frame, text="Área:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(form_frame, width=30, state="readonly")
        self.area_combo.grid(row=0, column=1, padx=5, pady=5)
        
        areas = self.controller.get_all_areas(active_only=False)
        self.area_combo['values'] = [area.name for area in areas]
        
        # Texto de pregunta
        ttk.Label(form_frame, text="Texto:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.text_entry = tk.Text(form_frame, width=50, height=3)
        self.text_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activa", variable=self.active_var).grid(row=0, column=2, padx=5, pady=5)
        
        # Posiciones aplicables y penalizaciones
        penalties_frame = ttk.LabelFrame(form_frame, text="Posiciones Aplicables y Penalizaciones", padding="5")
        penalties_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        
        positions = ['Manager', 'Senior Manager', 'Analyst', 'Senior Analyst']
        self.penalty_entries = {}
        self.position_checkboxes = {}
        
        # Crear header
        ttk.Label(penalties_frame, text="Posición", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(penalties_frame, text="Aplicable", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(penalties_frame, text="Penalización", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5, pady=2)
        
        for i, pos in enumerate(positions, start=1):
            ttk.Label(penalties_frame, text=f"{pos}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Checkbox para indicar si la posición es aplicable
            var = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(penalties_frame, variable=var, command=lambda p=pos: self._toggle_penalty_entry(p))
            checkbox.grid(row=i, column=1, padx=5, pady=2)
            self.position_checkboxes[pos] = (var, checkbox)
            
            # Entry para penalización
            entry = ttk.Entry(penalties_frame, width=15, state='disabled')
            entry.insert(0, "0.0")
            entry.grid(row=i, column=2, padx=5, pady=2)
            self.penalty_entries[pos] = entry
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Importar CSV", command=self._import_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar CSV", command=self._export_csv).pack(side=tk.LEFT, padx=5)
        
        self.selected_id: Optional[int] = None
        
        # Lista de preguntas
        list_frame = ttk.LabelFrame(self.window, text="Preguntas Existentes", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Área', 'Texto', 'Activa')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=50)
        self.tree.heading('Área', text='Área')
        self.tree.column('Área', width=150)
        self.tree.heading('Texto', text='Texto')
        self.tree.column('Texto', width=400)
        self.tree.heading('Activa', text='Activa')
        self.tree.column('Activa', width=80)
        
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
    
    def _load_questions(self):
        """Carga las preguntas en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        questions = self.controller.get_all_questions(active_only=False)
        areas = {area.id: area.name for area in self.controller.get_all_areas(active_only=False)}
        
        for question in questions:
            area_name = areas.get(question.area_id, 'N/A')
            text_short = question.text[:80] + '...' if len(question.text) > 80 else question.text
            self.tree.insert('', tk.END, values=(
                question.id,
                area_name,
                text_short,
                'Sí' if question.active else 'No'
            ))
    
    def _toggle_penalty_entry(self, position: str):
        """Habilita o deshabilita el campo de penalización según el checkbox."""
        var, _ = self.position_checkboxes[position]
        entry = self.penalty_entries[position]
        
        if var.get():
            entry.config(state='normal')
        else:
            entry.config(state='disabled')
            entry.delete(0, tk.END)
            entry.insert(0, "0.0")
    
    def _on_select(self, event):
        """Maneja la selección de una pregunta."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            question = self.controller.get_question(self.selected_id)
            if question:
                areas = self.controller.get_all_areas(active_only=False)
                area_name = next((a.name for a in areas if a.id == question.area_id), '')
                self.area_combo.set(area_name)
                self.text_entry.delete('1.0', tk.END)
                self.text_entry.insert('1.0', question.text)
                self.active_var.set(question.active)
                
                # Cargar posiciones aplicables (solo las que tienen entrada en position_weights)
                for pos, entry in self.penalty_entries.items():
                    var, _ = self.position_checkboxes[pos]
                    has_position = pos in question.position_weights
                    var.set(has_position)
                    entry.config(state='normal' if has_position else 'disabled')
                    entry.delete(0, tk.END)
                    if has_position:
                        entry.insert(0, str(question.position_weights.get(pos, 0.0)))
                    else:
                        entry.insert(0, "0.0")
    
    def _create(self):
        """Crea una nueva pregunta."""
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El área es obligatoria")
            return
        
        text = self.text_entry.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Advertencia", "El texto de la pregunta es obligatorio")
            return
        
        areas = self.controller.get_all_areas(active_only=False)
        area_name = self.area_combo.get()
        area_id = next((a.id for a in areas if a.name == area_name), None)
        
        if not area_id:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        try:
            # Solo incluir posiciones marcadas como aplicables
            position_weights = {}
            for pos, entry in self.penalty_entries.items():
                var, _ = self.position_checkboxes[pos]
                if var.get():  # Solo si está marcada como aplicable
                    try:
                        penalty = float(entry.get())
                        if penalty < 0:
                            raise ValueError("Las penalizaciones deben ser >= 0")
                        position_weights[pos] = penalty
                    except ValueError:
                        messagebox.showerror("Error", f"Penalización inválida para {pos}")
                        return
            
            # Validar que al menos una posición esté seleccionada
            if not position_weights:
                messagebox.showwarning("Advertencia", "Debe seleccionar al menos una posición aplicable")
                return
            
            self.controller.create_question(area_id, text, self.active_var.get(), position_weights)
            messagebox.showinfo("Éxito", "Pregunta creada correctamente")
            self._clear_form()
            self._load_questions()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear pregunta: {str(e)}")
    
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
            messagebox.showwarning("Advertencia", "El texto de la pregunta es obligatorio")
            return
        
        areas = self.controller.get_all_areas(active_only=False)
        area_name = self.area_combo.get()
        area_id = next((a.id for a in areas if a.name == area_name), None)
        
        if not area_id:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        try:
            # Solo incluir posiciones marcadas como aplicables
            position_weights = {}
            for pos, entry in self.penalty_entries.items():
                var, _ = self.position_checkboxes[pos]
                if var.get():  # Solo si está marcada como aplicable
                    try:
                        penalty = float(entry.get())
                        if penalty < 0:
                            raise ValueError("Las penalizaciones deben ser >= 0")
                        position_weights[pos] = penalty
                    except ValueError:
                        messagebox.showerror("Error", f"Penalización inválida para {pos}")
                        return
            
            # Validar que al menos una posición esté seleccionada
            if not position_weights:
                messagebox.showwarning("Advertencia", "Debe seleccionar al menos una posición aplicable")
                return
            
            self.controller.update_question(
                self.selected_id, area_id, text, self.active_var.get(), position_weights
            )
            messagebox.showinfo("Éxito", "Pregunta actualizada correctamente")
            self._clear_form()
            self._load_questions()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar pregunta: {str(e)}")
    
    def _delete(self):
        """Elimina una pregunta."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione una pregunta para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta pregunta?"):
            try:
                self.controller.delete_question(self.selected_id)
                messagebox.showinfo("Éxito", "Pregunta eliminada correctamente")
                self._clear_form()
                self._load_questions()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar pregunta: {str(e)}")
    
    def _edit(self):
        """Habilita edición de la pregunta seleccionada."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione una pregunta para editar")
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.area_combo.set('')
        self.text_entry.delete('1.0', tk.END)
        self.active_var.set(True)
        
        # Limpiar checkboxes y entries
        for pos, entry in self.penalty_entries.items():
            var, _ = self.position_checkboxes[pos]
            var.set(False)
            entry.config(state='disabled')
            entry.delete(0, tk.END)
            entry.insert(0, "0.0")
        
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())
    
    def _import_csv(self):
        """Importa preguntas desde CSV."""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                count = self.controller.import_questions_from_csv(filepath)
                messagebox.showinfo("Éxito", f"Se importaron {count} preguntas")
                self._load_questions()
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar: {str(e)}")
    
    def _export_csv(self):
        """Exporta preguntas a CSV."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.controller.export_questions_to_csv(filepath)
                messagebox.showinfo("Éxito", f"Preguntas exportadas a {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

