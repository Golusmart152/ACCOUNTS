import customtkinter as ctk
from . import db_manager
from tkinter import filedialog, messagebox, W
import datetime
import os

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self, anchor="w")
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tab_view.add("Company Profile")
        self.tab_view.add("GST")
        self.tab_view.add("Documents")
        self.tab_view.add("Data Management")
        self.tab_view.add("Preferences")

        self.setting_vars = {}

        self.create_company_profile_tab(self.tab_view.tab("Company Profile"))
        self.create_gst_tab(self.tab_view.tab("GST"))
        self.create_documents_tab(self.tab_view.tab("Documents"))
        self.create_data_tab(self.tab_view.tab("Data Management"))
        self.create_preferences_tab(self.tab_view.tab("Preferences"))

        self.save_button = ctk.CTkButton(self, text="Save All Settings", command=self.save_settings)
        self.save_button.grid(row=1, column=0, padx=10, pady=10, sticky="e")

    def _create_setting_entry(self, parent, key, label_text, row):
        """Helper to create a label and an entry for a setting."""
        label = ctk.CTkLabel(parent, text=label_text, anchor=W)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        string_var = ctk.StringVar()
        entry = ctk.CTkEntry(parent, textvariable=string_var, width=300)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky="we")

        self.setting_vars[key] = string_var
        return entry

    def create_company_profile_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        self._create_setting_entry(tab, "company_name", "Business Name:", 0)
        self._create_setting_entry(tab, "company_address", "Address:", 1)
        self._create_setting_entry(tab, "company_gstin", "GSTIN:", 2)
        self._create_setting_entry(tab, "company_pan", "PAN:", 3)
        self._create_setting_entry(tab, "company_phone", "Contact Number:", 4)
        self._create_setting_entry(tab, "company_email", "Email:", 5)

        # Logo
        logo_entry = self._create_setting_entry(tab, "company_logo_path", "Logo File Path:", 6)
        logo_button = ctk.CTkButton(tab, text="Browse...", command=lambda: self.browse_file(logo_entry))
        logo_button.grid(row=6, column=2, padx=5, pady=5)

    def create_gst_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="GST Configuration", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=(10, 10), sticky="w")

        # --- Company State ---
        ctk.CTkLabel(tab, text="My Business State (for Tax Calculation):").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        indian_states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
            "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
            "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
            "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
            "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
            "Ladakh", "Lakshadweep", "Puducherry"
        ]

        self.setting_vars['company_state'] = ctk.StringVar()
        state_menu = ctk.CTkOptionMenu(tab, variable=self.setting_vars['company_state'], values=[""] + sorted(indian_states))
        state_menu.grid(row=1, column=1, padx=10, pady=5, sticky="we")

        # --- GST Slabs ---
        slabs_frame = ctk.CTkFrame(tab)
        slabs_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(20, 10))
        slabs_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(slabs_frame, text="GST Slabs", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, pady=5, padx=10, sticky="w")

        self.slabs_list_frame = ctk.CTkFrame(slabs_frame, fg_color="transparent")
        self.slabs_list_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5)

        # --- Add New Slab ---
        add_frame = ctk.CTkFrame(slabs_frame)
        add_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(5, 10))

        ctk.CTkLabel(add_frame, text="Add New Slab:").pack(side="left", padx=(5,10))
        self.new_slab_rate = ctk.CTkEntry(add_frame, placeholder_text="Rate (%)")
        self.new_slab_rate.pack(side="left", padx=5)
        self.new_slab_desc = ctk.CTkEntry(add_frame, placeholder_text="Description (e.g., GST 5%)", width=200)
        self.new_slab_desc.pack(side="left", padx=5, expand=True, fill="x")
        add_button = ctk.CTkButton(add_frame, text="Add Slab", width=80, command=self._add_gst_slab)
        add_button.pack(side="left", padx=5)

        # We will call the refresh method in load_data, so it populates when the frame is shown

    def create_documents_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="Document Prefixes", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10,5), sticky="w")
        self._create_setting_entry(tab, "prefix_sales_invoice", "Sales Invoice Prefix:", 1)
        self._create_setting_entry(tab, "prefix_quotation", "Quotation Prefix:", 2)
        self._create_setting_entry(tab, "prefix_purchase_invoice", "Purchase Invoice Prefix:", 3)

        ctk.CTkLabel(tab, text="Bank Details for Invoices", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, columnspan=2, pady=(20,5), sticky="w")
        self._create_setting_entry(tab, "bank_account_name", "Account Name:", 5)
        self._create_setting_entry(tab, "bank_account_number", "Account Number:", 6)
        self._create_setting_entry(tab, "bank_ifsc_code", "IFSC Code:", 7)

        ctk.CTkLabel(tab, text="Terms & Conditions", font=ctk.CTkFont(weight="bold")).grid(row=8, column=0, columnspan=2, pady=(20,5), sticky="w")
        self.terms_textbox = ctk.CTkTextbox(tab, height=150)
        self.terms_textbox.grid(row=9, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        # Note: CTkTextbox doesn't have a simple textvariable, so we handle it separately.

    def create_data_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)

        backup_frame = ctk.CTkFrame(tab)
        backup_frame.pack(fill="x", padx=10, pady=10)
        backup_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(backup_frame, text="Manual Backup & Restore", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(backup_frame, text="Backup the current database to a safe location or restore from a previous backup.").pack(anchor="w", padx=10, pady=5)

        button_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(button_frame, text="Backup Now...", command=self.backup_database).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Restore from Backup...", command=self.restore_database).pack(side="left", padx=5)

        # Auto-backup (UI only for now)
        auto_backup_frame = ctk.CTkFrame(tab)
        auto_backup_frame.pack(fill="x", padx=10, pady=10, expand=True)
        auto_backup_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(auto_backup_frame, text="Automatic Backups", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=5)
        self._create_setting_entry(auto_backup_frame, "auto_backup_path", "Auto-backup Folder:", 1)
        self.setting_vars['auto_backup_enabled'] = ctk.StringVar(value="0")
        ctk.CTkCheckBox(auto_backup_frame, text="Enable auto-backup on application close", variable=self.setting_vars['auto_backup_enabled'], onvalue="1", offvalue="0").grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="w")


    def create_preferences_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="Financial Year", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10,5), sticky="w")
        self._create_setting_entry(tab, "financial_year_start", "Start Date (YYYY-MM-DD):", 1)
        self._create_setting_entry(tab, "financial_year_end", "End Date (YYYY-MM-DD):", 2)

        ctk.CTkLabel(tab, text="Application Startup", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, columnspan=2, pady=(20,5), sticky="w")

        # This should be populated from the actual frames in main.py ideally
        startup_screens = ["Dashboard", "New Sale", "New Purchase", "Universal Search"]
        self.setting_vars['default_startup_screen'] = ctk.StringVar()
        ctk.CTkOptionMenu(tab, variable=self.setting_vars['default_startup_screen'], values=startup_screens).grid(row=4, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(tab, text="Default Startup Screen:").grid(row=4, column=0, padx=10, pady=5, sticky="w")

    def browse_file(self, entry_widget):
        path = filedialog.askopenfilename(title="Select Logo File", filetypes=(("Image Files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")))
        if path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def load_data(self):
        """Load all settings from DB and populate the form."""
        all_settings = db_manager.get_all_settings()
        for key, var in self.setting_vars.items():
            var.set(all_settings.get(key, ""))

        self.terms_textbox.delete("1.0", "end")
        self.terms_textbox.insert("1.0", all_settings.get("doc_terms_conditions", ""))

        self.refresh_gst_slabs_list()

    def save_settings(self):
        """Save all settings from the form to the DB."""
        try:
            for key, var in self.setting_vars.items():
                db_manager.set_setting(key, var.get())

            # Handle textbox separately
            db_manager.set_setting("doc_terms_conditions", self.terms_textbox.get("1.0", "end-1c"))

            messagebox.showinfo("Success", "Settings saved successfully.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}", parent=self)

    def refresh_gst_slabs_list(self):
        """Clears and re-populates the list of GST slabs from the database."""
        # Clear existing widgets
        for widget in self.slabs_list_frame.winfo_children():
            widget.destroy()

        try:
            # This function will be created in db_manager.py
            slabs = db_manager.get_all_gst_slabs()

            # Header
            ctk.CTkLabel(self.slabs_list_frame, text="Rate (%)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.slabs_list_frame, text="Description", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=2, sticky="w")

            if not slabs:
                ctk.CTkLabel(self.slabs_list_frame, text="No GST slabs configured.").grid(row=1, column=0, columnspan=3, padx=10, pady=5)
                return

            for i, slab in enumerate(slabs):
                rate_label = ctk.CTkLabel(self.slabs_list_frame, text=f"{slab['rate']:.2f}")
                rate_label.grid(row=i + 1, column=0, padx=10, pady=2, sticky="w")

                desc_label = ctk.CTkLabel(self.slabs_list_frame, text=slab['description'])
                desc_label.grid(row=i + 1, column=1, padx=10, pady=2, sticky="w")

                # Don't allow deleting the 0% slab
                if slab['rate'] != 0:
                    delete_button = ctk.CTkButton(
                        self.slabs_list_frame, text="Delete", fg_color="#D32F2F", hover_color="#C62828",
                        width=60, command=lambda s_id=slab['id']: self._delete_gst_slab(s_id)
                    )
                    delete_button.grid(row=i + 1, column=2, padx=10, pady=2)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GST slabs: {e}", parent=self)
            ctk.CTkLabel(self.slabs_list_frame, text=f"Error loading slabs.").grid(row=0, column=0)

    def _add_gst_slab(self):
        """Handles adding a new GST slab to the database."""
        rate_str = self.new_slab_rate.get()
        description = self.new_slab_desc.get()

        if not rate_str or not description:
            messagebox.showwarning("Input Error", "Please provide both a rate and a description.", parent=self)
            return

        try:
            rate = float(rate_str)
            # This function will be created in db_manager.py
            db_manager.add_gst_slab(rate, description)

            self.new_slab_rate.delete(0, "end")
            self.new_slab_desc.delete(0, "end")
            self.refresh_gst_slabs_list()
            messagebox.showinfo("Success", f"GST Slab {rate}% added successfully.", parent=self)
        except ValueError:
            messagebox.showerror("Input Error", "Rate must be a valid number.", parent=self)
        except Exception as e:
            # A more specific error check for UNIQUE constraint would be good here
            if "UNIQUE constraint failed" in str(e):
                messagebox.showerror("Database Error", f"A GST slab with rate '{rate}' already exists.", parent=self)
            else:
                messagebox.showerror("Database Error", f"Failed to add GST slab: {e}", parent=self)

    def _delete_gst_slab(self, slab_id):
        """Handles deleting a GST slab from the database."""
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this GST slab? This action cannot be undone.", icon="warning", parent=self):
            return

        try:
            # This function will be created in db_manager.py
            db_manager.delete_gst_slab(slab_id)
            self.refresh_gst_slabs_list()
            messagebox.showinfo("Success", "GST Slab deleted successfully.", parent=self)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete GST slab: {e}", parent=self)

    def backup_database(self):
        """Handles the UI for backing up the database."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        suggested_filename = f"fastfin-backup-{timestamp}.db"

        backup_path = filedialog.asksaveasfilename(
            title="Save Database Backup",
            initialfile=suggested_filename,
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            parent=self
        )
        if not backup_path:
            return

        if db_manager.backup_database(backup_path):
            messagebox.showinfo("Success", f"Database backed up successfully to:\n{backup_path}", parent=self)
        else:
            messagebox.showerror("Error", "Failed to back up the database.", parent=self)

    def restore_database(self):
        """Handles the UI for restoring the database."""
        warning_message = (
            "WARNING: Restoring from a backup will completely overwrite all current data. "
            "This action cannot be undone.\n\n"
            "It is recommended to create a backup of the current state before restoring.\n\n"
            "Do you want to proceed?"
        )
        if not messagebox.askyesno("Confirm Restore", warning_message, icon='warning', parent=self):
            return

        backup_path = filedialog.askopenfilename(
            title="Select Backup File to Restore",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            parent=self
        )
        if not backup_path:
            return

        if db_manager.restore_database(backup_path):
            messagebox.showinfo("Success", "Database restored successfully.\nThe application should be restarted for changes to take full effect.", parent=self)
        else:
            messagebox.showerror("Error", "Failed to restore the database.", parent=self)
