import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager

class UnitFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container frame
        main_view = ctk.CTkFrame(self)
        main_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_view.grid_columnconfigure(0, weight=1)
        main_view.grid_columnconfigure(1, weight=1)
        main_view.grid_rowconfigure(0, weight=1)

        self.create_simple_unit_widgets(main_view)
        self.create_compound_unit_widgets(main_view)

    def create_simple_unit_widgets(self, parent):
        simple_frame = ctk.CTkFrame(parent)
        simple_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        simple_frame.grid_columnconfigure(0, weight=1)
        simple_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(simple_frame, text="Manage Simple Units", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Form for adding new simple units
        form_frame = ctk.CTkFrame(simple_frame, fg_color="transparent")
        form_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        self.simple_unit_name_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter new unit name (e.g., 'Gram')")
        self.simple_unit_name_entry.grid(row=0, column=0, padx=(0,5), pady=5, sticky="ew")
        self.add_simple_unit_button = ctk.CTkButton(form_frame, text="Add Unit", command=self.add_simple_unit)
        self.add_simple_unit_button.grid(row=0, column=1, pady=5, sticky="e")

        # Treeview for simple units
        self.simple_units_tree = ttk.Treeview(simple_frame, columns=("id", "name"), show="headings")
        self.simple_units_tree.heading("id", text="ID")
        self.simple_units_tree.heading("name", text="Unit Name")
        self.simple_units_tree.column("id", width=50)
        self.simple_units_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

    def create_compound_unit_widgets(self, parent):
        compound_frame = ctk.CTkFrame(parent)
        compound_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        compound_frame.grid_columnconfigure(0, weight=1)
        compound_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(compound_frame, text="Manage Compound Units", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # Form for adding compound units
        form_frame = ctk.CTkFrame(compound_frame, fg_color="transparent")
        form_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="1").grid(row=0, column=0, padx=5)
        self.base_unit_var = ctk.StringVar()
        self.base_unit_menu = ctk.CTkOptionMenu(form_frame, variable=self.base_unit_var, values=[])
        self.base_unit_menu.grid(row=0, column=1, padx=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="=").grid(row=0, column=2, padx=5)
        self.conversion_factor_entry = ctk.CTkEntry(form_frame, width=80)
        self.conversion_factor_entry.grid(row=0, column=3, padx=5)

        self.secondary_unit_var = ctk.StringVar()
        self.secondary_unit_menu = ctk.CTkOptionMenu(form_frame, variable=self.secondary_unit_var, values=[])
        self.secondary_unit_menu.grid(row=0, column=4, padx=5, sticky="ew")

        self.add_compound_button = ctk.CTkButton(form_frame, text="Add Relationship", command=self.add_compound_unit)
        self.add_compound_button.grid(row=0, column=5, padx=5)

        # Treeview for compound units
        columns = ("id", "base", "factor", "secondary")
        self.compound_units_tree = ttk.Treeview(compound_frame, columns=columns, show="headings")
        self.compound_units_tree.heading("id", text="ID")
        self.compound_units_tree.heading("base", text="Base Unit")
        self.compound_units_tree.heading("factor", text="Factor")
        self.compound_units_tree.heading("secondary", text="Secondary Unit")
        self.compound_units_tree.column("id", width=50)
        self.compound_units_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

    def load_data(self):
        # Load simple units
        for item in self.simple_units_tree.get_children():
            self.simple_units_tree.delete(item)
        self.all_units = db_manager.get_all_units()
        unit_names = []
        self.unit_map = {}
        for unit in self.all_units:
            self.simple_units_tree.insert("", "end", values=(unit['id'], unit['name']))
            unit_names.append(unit['name'])
            self.unit_map[unit['name']] = unit['id']

        # Update option menus
        self.base_unit_menu.configure(values=unit_names)
        self.secondary_unit_menu.configure(values=unit_names)
        if unit_names:
            self.base_unit_var.set(unit_names[0])
            self.secondary_unit_var.set(unit_names[0])

        # Load compound units
        for item in self.compound_units_tree.get_children():
            self.compound_units_tree.delete(item)
        all_compound_units = db_manager.get_all_compound_units_display()
        for c_unit in all_compound_units:
            self.compound_units_tree.insert("", "end", values=(c_unit['id'], c_unit['base_unit_name'], c_unit['conversion_factor'], c_unit['secondary_unit_name']))


    def add_simple_unit(self):
        name = self.simple_unit_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Unit name cannot be empty.", parent=self)
            return
        if db_manager.add_unit(name):
            messagebox.showinfo("Success", f"Unit '{name}' added successfully.", parent=self)
            self.simple_unit_name_entry.delete(0, "end")
            self.load_data()
        else:
            messagebox.showerror("Error", f"Unit '{name}' may already exist.", parent=self)

    def add_compound_unit(self):
        try:
            base_unit_name = self.base_unit_var.get()
            secondary_unit_name = self.secondary_unit_var.get()
            factor = float(self.conversion_factor_entry.get())

            if not base_unit_name or not secondary_unit_name:
                messagebox.showerror("Error", "Please select both a base and secondary unit.", parent=self)
                return

            if base_unit_name == secondary_unit_name:
                messagebox.showerror("Error", "Base and secondary units cannot be the same.", parent=self)
                return

            base_unit_id = self.unit_map[base_unit_name]
            secondary_unit_id = self.unit_map[secondary_unit_name]

            if db_manager.add_compound_unit(base_unit_id, secondary_unit_id, factor):
                messagebox.showinfo("Success", "Compound unit relationship added.", parent=self)
                self.load_data()
            else:
                messagebox.showerror("Error", "Could not add compound unit relationship.", parent=self)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the conversion factor.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self)
