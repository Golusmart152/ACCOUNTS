import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager

class SupplierFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()
        self.load_suppliers()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Manage Suppliers", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        form_frame = ctk.CTkFrame(content_frame)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # Column 0
        ctk.CTkLabel(form_frame, text="Supplier Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="GSTIN:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.gstin_entry = ctk.CTkEntry(form_frame)
        self.gstin_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Address:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.address_entry = ctk.CTkEntry(form_frame)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Column 2
        ctk.CTkLabel(form_frame, text="Phone:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.phone_entry = ctk.CTkEntry(form_frame)
        self.phone_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Email:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.email_entry = ctk.CTkEntry(form_frame)
        self.email_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=3, column=3, padx=10, pady=10, sticky="e")
        self.add_button = ctk.CTkButton(button_frame, text="Add Supplier", command=self.add_supplier)
        self.add_button.pack(side="left", padx=5)
        self.update_button = ctk.CTkButton(button_frame, text="Update Selected", command=self.update_supplier, state="disabled")
        self.update_button.pack(side="left", padx=5)
        self.clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Treeview
        tree_container = ctk.CTkFrame(content_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "name", "gstin", "phone", "email", "address")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("address", width=200)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def get_form_data(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Supplier Name is required.")
            return None
        return (
            name,
            self.gstin_entry.get().strip(),
            self.address_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.email_entry.get().strip()
        )

    def load_suppliers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        suppliers = db_manager.get_all_suppliers()
        for supplier in suppliers:
            self.tree.insert("", "end", values=tuple(supplier))
        self.clear_form()

    def add_supplier(self):
        data = self.get_form_data()
        if data:
            if db_manager.add_supplier(*data):
                messagebox.showinfo("Success", "Supplier added successfully.")
                self.load_suppliers()
            else:
                messagebox.showerror("Database Error", f"Could not add supplier. '{data[0]}' may already exist.")

    def update_supplier(self):
        selected = self.tree.focus()
        if not selected: return

        supplier_id = self.tree.item(selected, "values")[0]
        data = self.get_form_data()
        if data:
            if db_manager.update_supplier(supplier_id, *data):
                messagebox.showinfo("Success", "Supplier updated successfully.")
                self.load_suppliers()
            else:
                messagebox.showerror("Database Error", "Could not update supplier.")

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.gstin_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.update_button.configure(state="disabled")
        self.add_button.configure(state="normal")
        self.name_entry.focus()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.clear_form()
            self.name_entry.insert(0, values[1])
            self.gstin_entry.insert(0, values[2])
            self.address_entry.insert(0, values[5]) # address is 6th col
            self.phone_entry.insert(0, values[3])
            self.email_entry.insert(0, values[4])

            self.update_button.configure(state="normal")
            self.add_button.configure(state="disabled")
        else:
            self.clear_form()

    def load_data(self):
        """Public method to be called when switching to this frame."""
        self.load_suppliers()
