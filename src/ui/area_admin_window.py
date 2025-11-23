"""Ventana de administración de Áreas."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional
from src.services.area_service import AreaService


class AreaAdminWindow(ttk.Frame):
    """Vista incrustada para CRUD de áreas."""
    
    def __init__(
        self,
        parent,
        area_service: AreaService,
        colors: Dict[str, str],
        on_back: Callable[[], None],
    ):
        super().__init__(parent, padding="20 20 20 15", style="Main.TFrame")
        self.area_service = area_service
        self.colors = colors
        self.on_back = on_back
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_areas()
    
    def _setup_ui(self):
        """Configura la interfaz incrustada."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(header, text="< Volver al Panel", command=self.on_back, style="Secondary.TButton").pack(side=tk.LEFT)
        
        ttk.Label(header, text="Administración de Áreas", style="HeaderTitle.TLabel").pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            header,
            text="Crea, actualiza y organiza las áreas activas para las evaluaciones.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W)
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(self, text="Nuevo/Editar Área", padding="15", style="Card.TLabelframe")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="Nombre:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=40, style="Main.TEntry")
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Descripción:", style="LabelCard.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.description_entry = tk.Text(form_frame, width=40, height=3, wrap=tk.WORD)
        self.description_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
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
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        # Lista de áreas
        list_frame = ttk.LabelFrame(self, text="Áreas Existentes", padding="15", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Nombre', 'Descripción', 'Activo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            width = 80 if col == 'ID' else 150
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
    
    def _load_areas(self):
        """Carga las áreas en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        areas = self.area_service.get_all_areas(active_only=False)
        
        for area in areas:
            desc_short = (area.description or '')[:50] + '...' if area.description and len(area.description) > 50 else (area.description or '')
            self.tree.insert('', tk.END, values=(
                area.id,
                area.name,
                desc_short,
                'Sí' if area.active else 'No'
            ))
    
    def _on_select(self, event):
        """Maneja la selección de un área."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            area = self.area_service.get_area(self.selected_id)
            if area:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, area.name)
                self.description_entry.delete('1.0', tk.END)
                if area.description:
                    self.description_entry.insert('1.0', area.description)
                self.active_var.set(area.active)
    
    def _create(self):
        """Crea una nueva área."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        description = self.description_entry.get('1.0', tk.END).strip() or None
        
        try:
            self.area_service.create_area(
                name=name,
                description=description,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Área creada correctamente")
            self._clear_form()
            self._load_areas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear: {str(e)}")
    
    def _update(self):
        """Actualiza un área."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un área para editar")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        description = self.description_entry.get('1.0', tk.END).strip() or None
        
        try:
            self.area_service.update_area(
                area_id=self.selected_id,
                name=name,
                description=description,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Área actualizada correctamente")
            self._clear_form()
            self._load_areas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _delete(self):
        """Elimina un área."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un área para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar esta área?"):
            try:
                self.area_service.delete_area(self.selected_id)
                messagebox.showinfo("Éxito", "Área eliminada correctamente")
                self._clear_form()
                self._load_areas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def _edit(self):
        """Habilita edición del elemento seleccionado."""
        self._on_select(None)
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete('1.0', tk.END)
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

