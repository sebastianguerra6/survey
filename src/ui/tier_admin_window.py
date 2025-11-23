"""Ventana de administración de Tiers."""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from typing import Callable, Dict, Optional
from src.services.tier_service import TierService
from src.services.area_service import AreaService


class TierAdminWindow(ttk.Frame):
    """Vista incrustada para crear y administrar tiers por área."""
    
    def __init__(
        self,
        parent,
        tier_service: TierService,
        area_service: AreaService,
        colors: Dict[str, str],
        on_back: Callable[[], None],
    ):
        super().__init__(parent, padding="20 20 20 15", style="Main.TFrame")
        self.tier_service = tier_service
        self.area_service = area_service
        self.colors = colors
        self.on_back = on_back
        
        self.selected_tier_id: Optional[int] = None
        self.area_map = {}
        
        self._setup_ui()
        self._load_areas()
    
    def _setup_ui(self):
        """Configura la interfaz."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(header, text="< Volver al Panel", command=self.on_back, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Label(header, text="Administración de Tiers", style="HeaderTitle.TLabel").pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            header,
            text="Define los rangos de puntaje y colores por área para clasificar resultados.",
            style="HeaderSubtitle.TLabel"
        ).pack(anchor=tk.W)
        
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill=tk.BOTH, expand=True)
        
        area_frame = ttk.LabelFrame(container, text="Área", padding="15", style="Card.TLabelframe")
        area_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(area_frame, text="Área:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.area_var = tk.StringVar()
        self.area_combo = ttk.Combobox(area_frame, textvariable=self.area_var, state="readonly", width=40, style="Main.TCombobox")
        self.area_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.area_combo.bind('<<ComboboxSelected>>', lambda e: self._load_tiers())
        area_frame.columnconfigure(1, weight=1)
        
        form_frame = ttk.LabelFrame(container, text="Nuevo / Editar Tier", padding="15", style="Card.TLabelframe")
        form_frame.pack(fill=tk.X, pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Nombre del Tier:", style="LabelCard.TLabel").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30, style="Main.TEntry")
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(form_frame, text="Rango de Puntaje (min-máx):", style="LabelCard.TLabel").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        range_frame = ttk.Frame(form_frame, style="Main.TFrame")
        range_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.min_entry = ttk.Entry(range_frame, width=10, style="Main.TEntry")
        self.min_entry.pack(side=tk.LEFT)
        ttk.Label(range_frame, text=" - ").pack(side=tk.LEFT)
        self.max_entry = ttk.Entry(range_frame, width=10, style="Main.TEntry")
        self.max_entry.pack(side=tk.LEFT)
        
        ttk.Label(form_frame, text="Descripción:", style="LabelCard.TLabel").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.description_text = tk.Text(form_frame, width=40, height=3, wrap=tk.WORD)
        self.description_text.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        self.description_text.configure(
            bg="#f8fafc",
            relief="flat",
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["accent"],
            font=("Segoe UI", 10),
            padx=8,
            pady=6
        )
        
        ttk.Label(form_frame, text="Color (opcional):", style="LabelCard.TLabel").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        color_frame = ttk.Frame(form_frame, style="Main.TFrame")
        color_frame.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.color_entry = ttk.Entry(color_frame, width=12, style="Main.TEntry")
        self.color_entry.pack(side=tk.LEFT)
        ttk.Button(color_frame, text="Seleccionar", command=self._pick_color, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form_frame, text="Activo", variable=self.active_var, style="Main.TCheckbutton").grid(row=0, column=2, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame, style="Main.TFrame")
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        ttk.Button(button_frame, text="Crear", command=self._create, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar", command=self._update, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self._delete, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(container, text="Tiers configurados", padding="15", style="Card.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("id", "nombre", "rango", "color", "activo", "descripcion")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        headings = {
            "id": "ID",
            "nombre": "Nombre",
            "rango": "Rango",
            "color": "Color",
            "activo": "Activo",
            "descripcion": "Descripción"
        }
        widths = {
            "id": 60,
            "nombre": 150,
            "rango": 140,
            "color": 100,
            "activo": 80,
            "descripcion": 260
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=tk.CENTER if col in ("id", "rango", "color", "activo") else tk.W)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def _load_areas(self):
        """Carga las áreas en el combo."""
        areas = self.area_service.get_all_areas(active_only=False)
        self.area_map = {area.name: area.id for area in areas}
        area_names = list(self.area_map.keys())
        self.area_combo['values'] = area_names
        if area_names:
            self.area_combo.current(0)
            self._load_tiers()
        else:
            messagebox.showwarning("Advertencia", "No hay áreas disponibles. Cree un área primero.")
    
    def _get_selected_area_id(self) -> Optional[int]:
        """Obtiene el ID del área seleccionada."""
        area_name = self.area_var.get()
        return self.area_map.get(area_name)
    
    def _load_tiers(self):
        """Carga los tiers del área seleccionada."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        area_id = self._get_selected_area_id()
        if not area_id:
            return
        
        tiers = self.tier_service.get_tiers(area_id=area_id, active_only=False)
        for tier in tiers:
            rango = f"{tier.min_score:.2f} - {tier.max_score:.2f}"
            self.tree.insert(
                '',
                tk.END,
                values=(
                    tier.id,
                    tier.name,
                    rango,
                    tier.color or "-",
                    "Sí" if tier.active else "No",
                    (tier.description or '')[:80]
                )
            )
    
    def _pick_color(self):
        """Selector de color."""
        color = colorchooser.askcolor(title="Seleccionar color del tier")
        if color and color[1]:
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color[1])
    
    def _read_form(self):
        """Lee los datos del formulario."""
        area_id = self._get_selected_area_id()
        if not area_id:
            raise ValueError("Seleccione un área")
        
        name = self.name_entry.get().strip()
        if not name:
            raise ValueError("El nombre del tier es obligatorio")
        
        try:
            min_score = float(self.min_entry.get())
            max_score = float(self.max_entry.get())
        except ValueError:
            raise ValueError("Los puntajes deben ser números")
        
        if min_score < 0 or max_score > 100:
            raise ValueError("Los puntajes deben estar entre 0 y 100")
        if min_score > max_score:
            raise ValueError("El puntaje mínimo no puede ser mayor al máximo")
        
        description = self.description_text.get('1.0', tk.END).strip() or None
        color = self.color_entry.get().strip() or None
        active = self.active_var.get()
        
        return area_id, name, min_score, max_score, description, color, active
    
    def _create(self):
        """Crea un nuevo tier."""
        try:
            data = self._read_form()
            self.tier_service.create_tier(*data)
            messagebox.showinfo("Éxito", "Tier creado correctamente")
            self._clear_form()
            self._load_tiers()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
    
    def _update(self):
        """Actualiza el tier seleccionado."""
        if not self.selected_tier_id:
            messagebox.showwarning("Advertencia", "Seleccione un tier para actualizar")
            return
        try:
            data = self._read_form()
            self.tier_service.update_tier(self.selected_tier_id, *data)
            messagebox.showinfo("Éxito", "Tier actualizado correctamente")
            self._clear_form()
            self._load_tiers()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
    
    def _delete(self):
        """Desactiva el tier seleccionado."""
        if not self.selected_tier_id:
            messagebox.showwarning("Advertencia", "Seleccione un tier para eliminar")
            return
        if messagebox.askyesno("Confirmar", "¿Desea desactivar este tier?"):
            try:
                self.tier_service.delete_tier(self.selected_tier_id)
                messagebox.showinfo("Éxito", "Tier desactivado correctamente")
                self._clear_form()
                self._load_tiers()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
    
    def _on_select(self, event):
        """Llena el formulario con el tier seleccionado."""
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        tier_id = item['values'][0]
        tier = self.tier_service.get_tier(tier_id)
        if not tier:
            return
        self.selected_tier_id = tier.id
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, tier.name)
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, f"{tier.min_score:.2f}")
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, f"{tier.max_score:.2f}")
        self.description_text.delete('1.0', tk.END)
        if tier.description:
            self.description_text.insert('1.0', tier.description)
        self.color_entry.delete(0, tk.END)
        if tier.color:
            self.color_entry.insert(0, tier.color)
        self.active_var.set(tier.active)
    
    def _clear_form(self):
        """Limpia los campos."""
        self.selected_tier_id = None
        self.name_entry.delete(0, tk.END)
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)
        self.description_text.delete('1.0', tk.END)
        self.color_entry.delete(0, tk.END)
        self.active_var.set(True)
        self.tree.selection_remove(self.tree.selection())

