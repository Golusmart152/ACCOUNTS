import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

class AssemblyFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.available_components = []
        self.build_components = {} # Using dict to prevent duplicates: {serial_id: data}
        self.create_widgets()
        self.load_available_components()

    def create_widgets(self):
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Create Assembly (Build a PC)", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        # --- Left Panel: Available Components ---
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left_frame, text="Available Components").pack(pady=5)

        self.search_entry = ctk.CTkEntry(left_frame, placeholder_text="Search components...")
        self.search_entry.pack(padx=5, pady=5, fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_components)

        self.available_tree = self.create_treeview(left_frame, ("ID", "Name", "Serial #"))

        # --- Middle Panel: Action Buttons ---
        middle_frame = ctk.CTkFrame(self)
        middle_frame.grid(row=1, column=1, padx=5, pady=10, sticky="ns")
        self.add_button = ctk.CTkButton(middle_frame, text=">>", command=self.add_to_build, width=40)
        self.add_button.pack(pady=20, padx=5)
        self.remove_button = ctk.CTkButton(middle_frame, text="<<", command=self.remove_from_build, width=40)
        self.remove_button.pack(pady=5, padx=5)

        # --- Right Panel: Current Build ---
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(right_frame, text="New PC Build").pack(pady=5)

        self.build_tree = self.create_treeview(right_frame, ("ID", "Name", "Serial #"))

        build_details_frame = ctk.CTkFrame(right_frame)
        build_details_frame.pack(pady=10, padx=5, fill="x")
        ctk.CTkLabel(build_details_frame, text="Assembled PC Name:").pack(side="left", padx=5)
        self.build_name_entry = ctk.CTkEntry(build_details_frame, placeholder_text="e.g., Customer John Doe PC")
        self.build_name_entry.pack(side="left", padx=5, expand=True, fill="x")

        self.total_cost_label = ctk.CTkLabel(build_details_frame, text="Total Cost: ₹0.00", font=ctk.CTkFont(weight="bold"))
        self.total_cost_label.pack(side="left", padx=10)

        self.create_build_button = ctk.CTkButton(right_frame, text="Create Assembly", command=self.create_assembly)
        self.create_build_button.pack(pady=10, padx=5, side="bottom", fill="x")

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.column(columns[0], width=50, anchor="center")
        tree.column(columns[1], width=150)
        tree.column(columns[2], width=150)
        tree.pack(padx=5, pady=5, fill="both", expand=True)
        return tree

    def load_available_components(self):
        self.available_components = db_manager.get_in_stock_serial_numbers()
        self.filter_components()

    def filter_components(self, event=None):
        search_term = self.search_entry.get().lower()
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        for comp in self.available_components:
            # Don't show components already in the build
            if comp['serial_id'] in self.build_components:
                continue
            if search_term in comp['item_name'].lower() or search_term in comp['serial_number'].lower():
                self.available_tree.insert("", "end", values=(comp['serial_id'], comp['item_name'], comp['serial_number']), iid=comp['serial_id'])

    def add_to_build(self):
        selected_ids = self.available_tree.selection()
        if not selected_ids: return

        for serial_id in selected_ids:
            # Find the component data
            comp_data = next((c for c in self.available_components if c['serial_id'] == int(serial_id)), None)
            if comp_data:
                self.build_components[comp_data['serial_id']] = comp_data

        self.refresh_build_tree()
        self.filter_components() # Refresh available list

    def remove_from_build(self):
        selected_ids = self.build_tree.selection()
        if not selected_ids: return

        for serial_id in selected_ids:
            if int(serial_id) in self.build_components:
                del self.build_components[int(serial_id)]

        self.refresh_build_tree()
        self.filter_components() # Refresh available list

    def refresh_build_tree(self):
        for item in self.build_tree.get_children():
            self.build_tree.delete(item)

        total_cost = 0.0
        for serial_id, comp in self.build_components.items():
            self.build_tree.insert("", "end", values=(comp['serial_id'], comp['item_name'], comp['serial_number']), iid=serial_id)
            total_cost += comp['purchase_price']

        self.total_cost_label.configure(text=f"Total Cost: ₹{total_cost:,.2f}")

    def create_assembly(self):
        build_name = self.build_name_entry.get().strip()
        if not build_name:
            messagebox.showerror("Error", "Please provide a name for the new assembled PC.")
            return

        if not self.build_components:
            messagebox.showerror("Error", "Please add at least one component to the build.")
            return

        component_ids = list(self.build_components.keys())

        new_serial = db_manager.create_assembly_transaction(build_name, component_ids)

        if new_serial:
            messagebox.showinfo("Success", f"Assembly created successfully!\nNew Serial Number: {new_serial}")
            self.build_components.clear()
            self.refresh_build_tree()
            self.load_available_components()
            self.build_name_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", "Failed to create assembly. Check logs for details.")

    def load_data(self):
        """Public method to be called when switching to this frame."""
        self.load_available_components()
        self.build_components.clear()
        self.refresh_build_tree()
        self.build_name_entry.delete(0, "end")
        self.search_entry.delete(0, "end")
