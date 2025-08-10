import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager

class GodownFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(self, text="Manage Godowns", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Main content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Form for adding/editing
        form_frame = ctk.CTkFrame(content_frame)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Godown Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Main Store")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Location:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.location_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., City Center")
        self.location_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        self.add_button = ctk.CTkButton(button_frame, text="Add Godown", command=self.add_godown)
        self.add_button.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(button_frame, text="Update Selected", command=self.update_godown, state="disabled")
        self.update_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Treeview for displaying godowns
        tree_container = ctk.CTkFrame(content_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "name", "location")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Godown Name")
        self.tree.heading("location", text="Location")
        self.tree.column("id", width=50, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_godowns()

    def load_godowns(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        godowns = db_manager.get_all_godowns()
        for godown in godowns:
            self.tree.insert("", "end", values=(godown['id'], godown['name'], godown['location']))
        self.clear_form()

    def add_godown(self):
        name = self.name_entry.get().strip()
        location = self.location_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Godown Name cannot be empty.")
            return
        if db_manager.add_godown(name, location):
            messagebox.showinfo("Success", "Godown added successfully.")
            self.load_godowns()
        else:
            messagebox.showerror("Database Error", f"Could not add godown. The name '{name}' may already exist.")

    def update_godown(self):
        selected_item = self.tree.focus()
        if not selected_item:
            return

        godown_id = self.tree.item(selected_item, "values")[0]
        name = self.name_entry.get().strip()
        location = self.location_entry.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Godown Name cannot be empty.")
            return

        if db_manager.update_godown(godown_id, name, location):
            messagebox.showinfo("Success", "Godown updated successfully.")
            self.load_godowns()
        else:
            messagebox.showerror("Database Error", "Could not update godown. The name may already exist.")

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.location_entry.delete(0, "end")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        self.update_button.configure(state="disabled")
        self.add_button.configure(state="normal")
        self.name_entry.focus()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, values[1])
            self.location_entry.delete(0, "end")
            self.location_entry.insert(0, values[2])
            self.update_button.configure(state="normal")
            self.add_button.configure(state="disabled")
        else:
            self.clear_form()
