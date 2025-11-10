"""Ventana de administración de Casos."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from src.services.case_service import CaseService
from src.services.area_service import AreaService


class CaseAdminWindow:
    """Ventana para CRUD de casos."""
    
    def __init__(self, parent, case_service: CaseService, area_service: AreaService):
        """Inicializa la ventana."""
        self.case_service = case_service
        self.area_service = area_service
        
        self.window = tk.Toplevel(parent)
        self.window.title("Administración de Casos")
        self.window.geometry("700x500")
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_areas()
        self._load_cases()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        # Frame de formulario
        form_frame = ttk.LabelFrame(self.window, text="Nuevo/Editar Caso", padding="10")
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Área
        ttk.Label(form_frame, text="Área:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(form_frame, width=37, state="readonly")
        self.area_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Nombre
        ttk.Label(form_frame, text="Nombre:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_entry = tk.Text(form_frame, width=40, height=3)
        self.description_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Activo
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var).grid(
            row=0, column=2, padx=5, pady=5
        )
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Lista de casos
        list_frame = ttk.LabelFrame(self.window, text="Casos Existentes", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Área', 'Nombre', 'Descripción', 'Activo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col == 'Área':
                self.tree.column(col, width=150)
            elif col == 'Nombre':
                self.tree.column(col, width=150)
            elif col == 'Descripción':
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=80)
        
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
        """Carga las áreas."""
        areas = self.area_service.get_all_areas(active_only=False)
        area_names = [a.name for a in areas]
        self.area_combo['values'] = area_names
    
    def _load_cases(self):
        """Carga los casos en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cases = self.case_service.get_all_cases(active_only=False)
        areas = {a.id: a.name for a in self.area_service.get_all_areas(active_only=False)}
        
        for case in cases:
            desc_short = (case.description or '')[:50] + '...' if case.description and len(case.description) > 50 else (case.description or '')
            area_name = areas.get(case.area_id, 'N/A')
            self.tree.insert('', tk.END, values=(
                case.id,
                area_name,
                case.name,
                desc_short,
                'Sí' if case.active else 'No'
            ))
    
    def _on_select(self, event):
        """Maneja la selección de un caso."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            case = self.case_service.get_case(self.selected_id)
            if case:
                # Cargar área
                areas = self.area_service.get_all_areas(active_only=False)
                area = next((a for a in areas if a.id == case.area_id), None)
                if area:
                    self.area_combo.set(area.name)
                
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, case.name)
                self.description_entry.delete('1.0', tk.END)
                if case.description:
                    self.description_entry.insert('1.0', case.description)
                self.active_var.set(case.active)
    
    def _create(self):
        """Crea un nuevo caso."""
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El área es obligatoria")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        # Obtener área ID
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        description = self.description_entry.get('1.0', tk.END).strip() or None
        
        try:
            self.case_service.create_case(
                area_id=area.id,
                name=name,
                description=description,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Caso creado correctamente")
            self._clear_form()
            self._load_cases()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear: {str(e)}")
    
    def _update(self):
        """Actualiza un caso."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un caso para editar")
            return
        
        if not self.area_combo.get():
            messagebox.showwarning("Advertencia", "El área es obligatoria")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        # Obtener área ID
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
            return
        
        description = self.description_entry.get('1.0', tk.END).strip() or None
        
        try:
            self.case_service.update_case(
                case_id=self.selected_id,
                area_id=area.id,
                name=name,
                description=description,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Caso actualizado correctamente")
            self._clear_form()
            self._load_cases()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _delete(self):
        """Elimina un caso."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un caso para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este caso?"):
            try:
                self.case_service.delete_case(self.selected_id)
                messagebox.showinfo("Éxito", "Caso eliminado correctamente")
                self._clear_form()
                self._load_cases()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def _edit(self):
        """Habilita edición del elemento seleccionado."""
        self._on_select(None)
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.area_combo.set('')
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete('1.0', tk.END)
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

