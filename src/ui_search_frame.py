import customtkinter as ctk
from tkinter import ttk
import db_manager

class SearchFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Frame for Search controls ---
        self.search_entry_frame = ctk.CTkFrame(self)
        self.search_entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.search_entry_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.search_entry_frame, text="Search Term:").grid(row=0, column=0, padx=10, pady=10)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.search_entry_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<Return>", self.perform_search)

        self.search_button = ctk.CTkButton(self.search_entry_frame, text="Search", command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Results Treeview ---
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Type", "Summary", "Details"), show="headings")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Summary", text="Summary")
        self.tree.heading("Details", text="Details")
        self.tree.column("Type", width=120, anchor='w')
        self.tree.column("Summary", width=300, anchor='w')
        self.tree.column("Details", width=400, anchor='w')

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbars
        yscroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscroll.set)

        xscroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=xscroll.set)


    def perform_search(self, event=None):
        search_term = self.search_var.get()
        if not search_term:
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch new results
        results = db_manager.universal_search(search_term)
        for res in results:
            self.tree.insert("", "end", values=(res['type'], res['summary'], res['details']))

    def load_data(self):
        # This can be used to clear the search when the frame is shown
        self.search_var.set("")
        for item in self.tree.get_children():
            self.tree.delete(item)
