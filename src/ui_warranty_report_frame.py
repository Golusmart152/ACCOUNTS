import customtkinter as ctk
from tkinter import ttk
from . import db_manager

class WarrantyReportFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Warranty Expiry Report", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Options Frame ---
        options_frame = ctk.CTkFrame(self)
        options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.days_ahead_var = ctk.StringVar(value="30")

        rb30 = ctk.CTkRadioButton(options_frame, text="Next 30 Days", variable=self.days_ahead_var, value="30", command=self.load_data)
        rb30.pack(side="left", padx=10)
        rb60 = ctk.CTkRadioButton(options_frame, text="Next 60 Days", variable=self.days_ahead_var, value="60", command=self.load_data)
        rb60.pack(side="left", padx=10)
        rb90 = ctk.CTkRadioButton(options_frame, text="Next 90 Days", variable=self.days_ahead_var, value="90", command=self.load_data)
        rb90.pack(side="left", padx=10)

        # --- Treeview for report ---
        tree_container = ctk.CTkFrame(self)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("item_name", "serial_number", "warranty_end_date", "customer_name", "invoice_number")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.grid(row=0, column=0, sticky="nsew")

    def load_data(self):
        """Public method to be called when switching to this frame."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        days = int(self.days_ahead_var.get())
        expiring_items = db_manager.get_expiring_warranties(days_ahead=days)

        for item in expiring_items:
            self.tree.insert("", "end", values=tuple(item))
