"""Ventana de administración de Perfiles."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional
from src.services.profile_service import ProfileService


class ProfileAdminWindow(ttk.Frame):
    """Vista incrustada para CRUD de perfiles."""
    
    def __init__(
        self,
        parent,
        profile_service: ProfileService,
        colors: Dict[str, str],
        on_back: Callable[[], None],
    ):
        super().__init__(parent, padding="20 20 20 15", style="Main.TFrame")
        self.profile_service = profile_service
        self.colors = colors
        self.on_back = on_back
        
        self.selected_id: Optional[int] = None
        
        self._setup_ui()
        self._load_profiles()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(header, text="< Volver al Panel", command=self.on_back, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Label(header, text="Administración de Perfiles", style="HeaderTitle.TLabel").pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            header,
            text="Define los perfiles disponibles para los evaluadores.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W)
        
        form_frame = ttk.LabelFrame(self, text="Nuevo/Editar Perfil", padding="15", style="Card.TLabelframe")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(form_frame, text="Nombre:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30, style="Main.TEntry")
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        form_frame.columnconfigure(1, weight=1)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var, style="Main.TCheckbutton").grid(
            row=0, column=2, padx=5, pady=5
        )
        
        button_frame = ttk.Frame(form_frame, style="Main.TFrame")
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Crear", command=self._create, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(self, text="Perfiles Existentes", padding="15", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Nombre', 'Activo')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        column_widths = {'ID': 80, 'Nombre': 200, 'Activo': 80}
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
    
    def _load_profiles(self):
        """Carga los perfiles en la lista."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        profiles = self.profile_service.get_all_profiles(active_only=False)
        
        for profile in profiles:
            self.tree.insert('', tk.END, values=(
                profile.id,
                profile.name,
                'Sí' if profile.active else 'No'
            ))
    
    def _on_select(self, event):
        """Maneja la selección de un perfil."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_id = item['values'][0]
            profile = self.profile_service.get_profile(self.selected_id)
            if profile:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, profile.name)
                self.active_var.set(profile.active)
    
    def _create(self):
        """Crea un nuevo perfil."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.profile_service.create_profile(name=name, active=self.active_var.get())
            messagebox.showinfo("Éxito", "Perfil creado correctamente")
            self._clear_form()
            self._load_profiles()
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear: {str(e)}")
    
    def _update(self):
        """Actualiza un perfil."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un perfil para editar")
            return
        
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio")
            return
        
        try:
            self.profile_service.update_profile(
                profile_id=self.selected_id,
                name=name,
                active=self.active_var.get()
            )
            messagebox.showinfo("Éxito", "Perfil actualizado correctamente")
            self._clear_form()
            self._load_profiles()
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _delete(self):
        """Elimina un perfil."""
        if not self.selected_id:
            messagebox.showwarning("Advertencia", "Seleccione un perfil para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este perfil?"):
            try:
                self.profile_service.delete_profile(self.selected_id)
                messagebox.showinfo("Éxito", "Perfil eliminado correctamente")
                self._clear_form()
                self._load_profiles()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def _edit(self):
        """Habilita edición del elemento seleccionado."""
        self._on_select(None)
    
    def _clear_form(self):
        """Limpia el formulario."""
        self.name_entry.delete(0, tk.END)
        self.active_var.set(True)
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

