import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

class HSNFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(self, text="HSN/SAC Code Management", font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # HSN Code List
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)

        self.hsn_tree = ttk.Treeview(self.tree_frame, columns=("ID", "HSN Code", "Description", "Default GST Rate"), show="headings")
        self.hsn_tree.grid(row=0, column=0, sticky="nsew")

        self.hsn_tree.heading("ID", text="ID")
        self.hsn_tree.heading("HSN Code", text="HSN/SAC Code")
        self.hsn_tree.heading("Description", text="Description")
        self.hsn_tree.heading("Default GST Rate", text="Default GST Rate")

        self.hsn_tree.column("ID", width=50, anchor="center")
        self.hsn_tree.column("HSN Code", width=150)
        self.hsn_tree.column("Description", width=300)
        self.hsn_tree.column("Default GST Rate", width=150, anchor="center")

        self.hsn_tree.bind("<<TreeviewSelect>>", self.on_hsn_select)

        # Input and Button Frame
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)
        self.form_frame.grid_columnconfigure(3, weight=1)

        # Form fields
        ctk.CTkLabel(self.form_frame, text="HSN/SAC Code:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hsn_code_entry = ctk.CTkEntry(self.form_frame)
        self.hsn_code_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.hsn_desc_entry = ctk.CTkEntry(self.form_frame)
        self.hsn_desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.form_frame, text="Default GST Slab:").grid(row=0, column=2, padx=(10, 5), pady=5, sticky="w")
        self.gst_slab_var = ctk.StringVar()
        self.gst_slab_menu = ctk.CTkOptionMenu(self.form_frame, variable=self.gst_slab_var, values=[])
        self.gst_slab_menu.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Buttons
        self.button_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, columnspan=4, pady=(10,5))

        self.add_button = ctk.CTkButton(self.button_frame, text="Add New", command=self.add_hsn)
        self.add_button.pack(side="left", padx=5)

        self.update_button = ctk.CTkButton(self.button_frame, text="Update Selected", command=self.update_hsn, state="disabled")
        self.update_button.pack(side="left", padx=5)

        self.delete_button = ctk.CTkButton(self.button_frame, text="Delete Selected", command=self.delete_hsn, state="disabled", fg_color="#D32F2F", hover_color="#C62828")
        self.delete_button.pack(side="left", padx=5)

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear Form", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        self.selected_hsn_id = None
        self.load_hsn_codes()
        self.load_gst_slabs()

    def load_hsn_codes(self):
        """Loads all HSN codes from the DB and populates the treeview."""
        for item in self.hsn_tree.get_children():
            self.hsn_tree.delete(item)

        try:
            self.hsn_codes_data = db_manager.get_all_hsn_codes_with_details()
            for code in self.hsn_codes_data:
                rate_display = f"{code['gst_rate']}%" if code['gst_rate'] is not None else "N/A"
                self.hsn_tree.insert("", "end", values=(code['id'], code['hsn_code'], code['description'], rate_display))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load HSN codes: {e}", parent=self)

    def load_gst_slabs(self):
        """Loads GST slabs and populates the option menu."""
        try:
            self.gst_slabs = db_manager.get_all_gst_slabs()
            self.gst_slab_map = {f"{slab['rate']}% - {slab['description']}": slab['id'] for slab in self.gst_slabs}
            self.gst_slab_id_map = {slab['id']: f"{slab['rate']}% - {slab['description']}" for slab in self.gst_slabs}

            slab_options = list(self.gst_slab_map.keys())
            self.gst_slab_menu.configure(values=slab_options)
            if slab_options:
                self.gst_slab_var.set(slab_options[0])
            else:
                self.gst_slab_var.set("No slabs configured")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GST slabs: {e}", parent=self)
            self.gst_slab_menu.configure(values=["Error"])

    def on_hsn_select(self, event=None):
        """Handles selection of an item in the treeview."""
        selected_items = self.hsn_tree.selection()
        if not selected_items:
            return

        selected_item = self.hsn_tree.item(selected_items[0])
        hsn_id = selected_item["values"][0]

        # Find the full data for the selected HSN code
        selected_hsn_data = next((c for c in self.hsn_codes_data if c['id'] == hsn_id), None)

        if selected_hsn_data:
            self.selected_hsn_id = selected_hsn_data['id']
            self.hsn_code_entry.delete(0, "end")
            self.hsn_code_entry.insert(0, selected_hsn_data['hsn_code'])
            self.hsn_desc_entry.delete(0, "end")
            self.hsn_desc_entry.insert(0, selected_hsn_data['description'])

            # Set the dropdown
            if selected_hsn_data['gst_slab_id'] in self.gst_slab_id_map:
                self.gst_slab_var.set(self.gst_slab_id_map[selected_hsn_data['gst_slab_id']])
            else:
                self.gst_slab_var.set("") # Or a default value

            self.update_button.configure(state="normal")
            self.delete_button.configure(state="normal")

    def add_hsn(self):
        """Adds a new HSN code to the database."""
        code = self.hsn_code_entry.get().strip()
        description = self.hsn_desc_entry.get().strip()
        selected_slab_str = self.gst_slab_var.get()

        if not code or not description:
            messagebox.showwarning("Input Error", "HSN Code and Description cannot be empty.", parent=self)
            return

        gst_slab_id = self.gst_slab_map.get(selected_slab_str)
        if gst_slab_id is None:
            messagebox.showwarning("Input Error", "Please select a valid GST Slab.", parent=self)
            return

        try:
            db_manager.add_hsn_code(code, description, gst_slab_id)
            messagebox.showinfo("Success", "HSN code added successfully.", parent=self)
            self.load_hsn_codes()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add HSN code: {e}", parent=self)

    def update_hsn(self):
        """Updates the selected HSN code in the database."""
        if self.selected_hsn_id is None:
            return

        code = self.hsn_code_entry.get().strip()
        description = self.hsn_desc_entry.get().strip()
        selected_slab_str = self.gst_slab_var.get()

        if not code or not description:
            messagebox.showwarning("Input Error", "HSN Code and Description cannot be empty.", parent=self)
            return

        gst_slab_id = self.gst_slab_map.get(selected_slab_str)
        if gst_slab_id is None:
            messagebox.showwarning("Input Error", "Please select a valid GST Slab.", parent=self)
            return

        try:
            db_manager.update_hsn_code(self.selected_hsn_id, code, description, gst_slab_id)
            messagebox.showinfo("Success", "HSN code updated successfully.", parent=self)
            self.load_hsn_codes()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update HSN code: {e}", parent=self)

    def delete_hsn(self):
        """Deletes the selected HSN code from the database."""
        if self.selected_hsn_id is None:
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this HSN code?", icon="warning", parent=self):
            return

        try:
            db_manager.delete_hsn_code(self.selected_hsn_id)
            messagebox.showinfo("Success", "HSN code deleted successfully.", parent=self)
            self.load_hsn_codes()
            self.clear_form()
        except ValueError as ve: # Catch the specific error for in-use codes
            messagebox.showerror("Deletion Failed", str(ve), parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete HSN code: {e}", parent=self)

    def clear_form(self):
        self.hsn_code_entry.delete(0, "end")
        self.hsn_desc_entry.delete(0, "end")
        self.gst_slab_var.set("")
        self.hsn_tree.selection_remove(self.hsn_tree.selection())
        self.selected_hsn_id = None
        self.update_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self.hsn_code_entry.focus()

    def load_data(self):
        """Public method to be called when the frame is shown."""
        self.load_hsn_codes()
        self.load_gst_slabs()
