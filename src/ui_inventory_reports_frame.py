import customtkinter as ctk
from tkinter import ttk
import db_manager

class InventoryReportsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Inventory Reports", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Report Selection ---
        report_frame = ctk.CTkFrame(self)
        report_frame.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        reports = ["Low Stock", "Stock by Category"]
        self.report_combo = ctk.CTkComboBox(report_frame, values=reports, command=self.load_report_data)
        self.report_combo.pack()
        self.report_combo.set("Low Stock")

        # --- Treeview for report ---
        self.tree = ttk.Treeview(self)
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def load_data(self):
        """Public method to be called when switching to this frame."""
        self.load_report_data()

    def load_report_data(self, report_type=None):
        if report_type is None:
            report_type = self.report_combo.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if report_type == "Low Stock":
            self.tree["columns"] = ("id", "name", "min_stock", "current_stock")
            for col in self.tree["columns"]: self.tree.heading(col, text=col.title())
            data = db_manager.get_low_stock_report()
            for row in data:
                # The current_stock is not calculated yet in the placeholder function
                self.tree.insert("", "end", values=(row['id'], row['name'], row['minimum_stock_level'], 'N/A'))

        elif report_type == "Stock by Category":
            self.tree["columns"] = ("category", "item_count")
            for col in self.tree["columns"]: self.tree.heading(col, text=col.title())
            data = db_manager.get_category_stock_report()
            for row in data:
                self.tree.insert("", "end", values=(row['category'], row['item_count']))
