"""Ventana de administración de Casos."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional
from src.services.case_service import CaseService
from src.services.area_service import AreaService


class CaseAdminWindow(ttk.Frame):
    """Vista incrustada para CRUD de casos."""
    
    def __init__(
        self,
        parent,
        case_service: CaseService,
        area_service: AreaService,
        colors: Dict[str, str],
        on_back: Callable[[], None],
    ):
        super().__init__(parent, padding="20 20 20 15", style="Main.TFrame")
        self.case_service = case_service
        self.area_service = area_service
        self.colors = colors
        self.on_back = on_back
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_areas()
        self._load_cases()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(header, text="< Volver al Panel", command=self.on_back, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Label(header, text="Administración de Casos", style="HeaderTitle.TLabel").pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            header,
            text="Relaciona los casos disponibles con sus áreas para el proceso de evaluación.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W)
        
        form_frame = ttk.LabelFrame(self, text="Nuevo/Editar Caso", padding="15", style="Card.TLabelframe")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Área:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_combo = ttk.Combobox(form_frame, state="readonly", style="Main.TCombobox")
        self.area_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Nombre:", style="LabelCard.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, style="Main.TEntry")
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Descripción:", style="LabelCard.TLabel").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_entry = tk.Text(form_frame, height=3, wrap=tk.WORD)
        self.description_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.description_entry.configure(
            bg="#f8fafc",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            font=("Segoe UI", 10),
            padx=8,
            pady=6
        )
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var, style="Main.TCheckbutton").grid(
            row=0, column=2, padx=5, pady=5
        )
        
        button_frame = ttk.Frame(form_frame, style="Main.TFrame")
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(self, text="Casos Existentes", padding="15", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Área', 'Nombre', 'Descripción', 'Activo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        column_widths = {'ID': 60, 'Área': 150, 'Nombre': 150, 'Descripción': 220, 'Activo': 80}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        action_frame = ttk.Frame(list_frame, style="Main.TFrame")
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Editar", command=self._edit, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar", command=self._delete, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
    
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
        
        area = self._get_selected_area()
        if not area:
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
        
        area = self._get_selected_area()
        if not area:
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
    
    def _get_selected_area(self):
        """Obtiene el objeto área a partir del combo."""
        area_name = self.area_combo.get()
        areas = self.area_service.get_all_areas(active_only=False)
        area = next((a for a in areas if a.name == area_name), None)
        if not area:
            messagebox.showerror("Error", "Área no encontrada")
        return area

