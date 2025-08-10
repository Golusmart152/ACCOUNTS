import customtkinter as ctk
from tkinter import ttk
import db_manager

class ChartOfAccountsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Chart of Accounts", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        tree_container = ctk.CTkFrame(self)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "name", "type", "predefined")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Account Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("predefined", text="Predefined")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250)
        self.tree.column("type", width=150)
        self.tree.column("predefined", width=100, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

    def load_data(self):
        """Public method to be called when switching to this frame."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        accounts = db_manager.get_all_accounts()
        for acc in accounts:
            self.tree.insert("", "end", values=(acc['id'], acc['name'], acc['type'], 'Yes' if acc['is_predefined'] else 'No'))
