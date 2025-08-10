import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import db_manager
import datetime

class AMCFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.selected_amc_id = None
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with title and view toggle
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="Annual Maintenance Contracts (AMCs)", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # View toggle buttons
        view_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        view_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        self.kanban_view_button = ctk.CTkButton(view_frame, text="Kanban View", command=self.show_kanban_view)
        self.kanban_view_button.pack(side="left", padx=5)
        
        self.table_view_button = ctk.CTkButton(view_frame, text="Table View", command=self.show_table_view)
        self.table_view_button.pack(side="left", padx=5)

        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Create both views
        self.create_kanban_view(content_frame)
        self.create_table_view(content_frame)
        
        # Show kanban view by default
        self.show_kanban_view()

    def create_kanban_view(self, parent):
        """Create a Kanban board for managing AMC contracts"""
        self.kanban_view_frame = ctk.CTkFrame(parent)
        self.kanban_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.kanban_view_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.kanban_view_frame.grid_rowconfigure(0, weight=1)
        
        # Kanban columns for different AMC statuses
        self.statuses = ["Active", "Expiring Soon", "Expired", "Renewed"]
        self.kanban_columns = {}
        
        for i, status in enumerate(self.statuses):
            column_frame = ctk.CTkFrame(self.kanban_view_frame, corner_radius=10)
            column_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            column_frame.grid_columnconfigure(0, weight=1)
            column_frame.grid_rowconfigure(1, weight=1)
            
            # Column header
            header_frame = ctk.CTkFrame(column_frame, height=40, corner_radius=10)
            header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            header_frame.grid_columnconfigure(0, weight=1)
            
            status_label = ctk.CTkLabel(header_frame, text=status, font=ctk.CTkFont(size=14, weight="bold"))
            status_label.pack(pady=10)
            
            # Scrollable content area for AMC cards
            content_frame = ctk.CTkScrollableFrame(column_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            content_frame.grid_columnconfigure(0, weight=1)
            
            self.kanban_columns[status] = content_frame
            
        # Add new AMC button at the bottom
        add_amc_frame = ctk.CTkFrame(self.kanban_view_frame)
        add_amc_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(add_amc_frame, text="+ Add New AMC", command=self.show_add_amc_dialog).pack(pady=10)
            
        # Load AMCs into kanban
        self.populate_kanban_view()
        
    def create_table_view(self, parent):
        """Create the traditional table view for AMCs"""
        self.table_view_frame = ctk.CTkFrame(parent)
        self.table_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.table_view_frame.grid_columnconfigure(0, weight=1)
        self.table_view_frame.grid_rowconfigure(2, weight=1)

        # Top frame for adding new AMCs
        add_amc_frame = ctk.CTkFrame(self.table_view_frame)
        add_amc_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.create_add_amc_form(add_amc_frame)

        # Bottom frame for lists
        lists_frame = ctk.CTkFrame(self.table_view_frame)
        lists_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_rowconfigure(0, weight=1)

        # AMC List
        amc_tree_frame = ctk.CTkFrame(lists_frame)
        amc_tree_frame.pack(side="top", fill="both", expand=True, pady=5)
        ctk.CTkLabel(amc_tree_frame, text="All AMCs").pack()
        columns = ("id", "customer", "start_date", "end_date", "value")
        self.amc_tree = ttk.Treeview(amc_tree_frame, columns=columns, show="headings")
        for col in columns: self.amc_tree.heading(col, text=col.replace('_',' ').title())
        self.amc_tree.pack(fill="both", expand=True)
        self.amc_tree.bind("<<TreeviewSelect>>", self.amc_selected)

        # Service Call List
        service_tree_frame = ctk.CTkFrame(lists_frame)
        service_tree_frame.pack(side="bottom", fill="both", expand=True, pady=5)

        service_header_frame = ctk.CTkFrame(service_tree_frame)
        service_header_frame.pack(fill="x")
        self.service_label = ctk.CTkLabel(service_header_frame, text="Service Calls for Selected AMC")
        self.service_label.pack(side="left")
        self.add_service_call_button = ctk.CTkButton(service_header_frame, text="Add Service Call", command=self.add_service_call, state="disabled")
        self.add_service_call_button.pack(side="right")

        sc_columns = ("id", "date", "details", "solution")
        self.service_tree = ttk.Treeview(service_tree_frame, columns=sc_columns, show="headings")
        for col in sc_columns: self.service_tree.heading(col, text=col.title())
        self.service_tree.pack(fill="both", expand=True)

    def show_kanban_view(self):
        """Show the kanban view and hide the table view"""
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid_remove()
        if hasattr(self, 'kanban_view_frame'):
            self.kanban_view_frame.grid()
        self.kanban_view_button.configure(state="disabled")
        self.table_view_button.configure(state="normal")
        self.current_view = "kanban"
        self.populate_kanban_view()
        
    def show_table_view(self):
        """Show the table view and hide the kanban view"""
        if hasattr(self, 'kanban_view_frame'):
            self.kanban_view_frame.grid_remove()
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid()
        self.table_view_button.configure(state="disabled")
        self.kanban_view_button.configure(state="normal")
        self.current_view = "table"
        self.load_table_data()

    def populate_kanban_view(self):
        """Populate the Kanban view with AMC contracts from database"""
        # Clear existing cards
        for status in self.kanban_columns:
            for widget in self.kanban_columns[status].winfo_children():
                widget.destroy()
                
        # Get AMCs from database
        amcs = db_manager.get_all_amcs()
        
        for amc in amcs:
            # Determine AMC status based on dates
            status = self.determine_amc_status(amc)
            self.add_amc_to_kanban(amc, status)

    def determine_amc_status(self, amc):
        """Determine the status of an AMC based on its dates"""
        try:
            end_date = datetime.datetime.strptime(amc[3], "%Y-%m-%d").date()  # end_date is index 3
            today = datetime.date.today()
            days_until_expiry = (end_date - today).days
            
            if days_until_expiry < 0:
                return "Expired"
            elif days_until_expiry <= 30:  # Expiring within 30 days
                return "Expiring Soon"
            else:
                return "Active"
        except (ValueError, TypeError):
            return "Active"  # Default status
            
    def add_amc_to_kanban(self, amc, status):
        """Add an AMC card to the appropriate Kanban column"""
        if status in self.kanban_columns:
            card_frame = ctk.CTkFrame(self.kanban_columns[status], corner_radius=8)
            card_frame.pack(fill="x", padx=5, pady=5)
            card_frame.grid_columnconfigure(0, weight=1)
            
            # AMC header
            header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            header_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(header_frame, text=f"AMC #{amc[0]}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(header_frame, text=f"₹{amc[4]:,.2f}", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, sticky="e")
            
            # AMC details
            ctk.CTkLabel(card_frame, text=f"Customer: {amc[1]}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card_frame, text=f"Start: {amc[2]}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card_frame, text=f"End: {amc[3]}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=2)
            
            # Calculate and show days remaining
            try:
                end_date = datetime.datetime.strptime(amc[3], "%Y-%m-%d").date()
                today = datetime.date.today()
                days_remaining = (end_date - today).days
                
                if days_remaining > 0:
                    ctk.CTkLabel(card_frame, text=f"Days remaining: {days_remaining}", 
                               font=ctk.CTkFont(size=11), text_color="orange" if days_remaining <= 30 else "green").pack(anchor="w", padx=10, pady=2)
                else:
                    ctk.CTkLabel(card_frame, text=f"Expired {abs(days_remaining)} days ago", 
                               font=ctk.CTkFont(size=11), text_color="red").pack(anchor="w", padx=10, pady=2)
            except (ValueError, TypeError):
                pass
            
            # Action buttons
            button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            ctk.CTkButton(button_frame, text="Service Calls", width=80, height=25, font=ctk.CTkFont(size=10),
                         command=lambda a=amc: self.show_service_calls(a)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="Add Service", width=80, height=25, font=ctk.CTkFont(size=10),
                         command=lambda a=amc: self.add_service_call_for_amc(a)).pack(side="left", padx=2)
            
            if status == "Expired":
                ctk.CTkButton(button_frame, text="Renew", width=60, height=25, font=ctk.CTkFont(size=10),
                             command=lambda a=amc: self.renew_amc(a), fg_color="green", hover_color="darkgreen").pack(side="left", padx=2)

    def show_service_calls(self, amc):
        """Show service calls for an AMC"""
        # Create service calls dialog
        service_window = ctk.CTkToplevel(self)
        service_window.title(f"Service Calls for AMC #{amc[0]}")
        service_window.geometry("600x400")
        service_window.transient(self)
        service_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(service_window)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header_frame, text=f"AMC #{amc[0]} - {amc[1]}", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="Add Service Call", command=lambda: self.add_service_call_for_amc(amc)).pack(side="right")
        
        # Service calls list
        calls_frame = ctk.CTkFrame(service_window)
        calls_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for service calls
        columns = ("id", "date", "details", "solution")
        service_tree = ttk.Treeview(calls_frame, columns=columns, show="headings")
        for col in columns: 
            service_tree.heading(col, text=col.title())
        service_tree.pack(fill="both", expand=True)
        
        # Load service calls
        calls = db_manager.get_service_calls_for_amc(amc[0])
        for call in calls: 
            service_tree.insert("", "end", values=tuple(call))
        
        # Close button
        ctk.CTkButton(service_window, text="Close", command=service_window.destroy).pack(pady=10)

    def add_service_call_for_amc(self, amc):
        """Add a service call for a specific AMC"""
        # Create service call dialog
        service_dialog = ctk.CTkToplevel(self)
        service_dialog.title(f"Add Service Call for AMC #{amc[0]}")
        service_dialog.geometry("400x300")
        service_dialog.transient(self)
        service_dialog.grab_set()
        
        # Form fields
        form_frame = ctk.CTkFrame(service_dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text=f"AMC: #{amc[0]} - {amc[1]}", font=ctk.CTkFont(weight="bold")).pack(pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Service Details:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        details_entry = ctk.CTkTextbox(form_frame, height=80)
        details_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="Solution Provided:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        solution_entry = ctk.CTkTextbox(form_frame, height=80)
        solution_entry.pack(fill="x", pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        def save_service_call():
            details = details_entry.get("1.0", "end-1c").strip()
            solution = solution_entry.get("1.0", "end-1c").strip()
            
            if details and solution:
                if db_manager.add_amc_service_call(amc[0], datetime.date.today().isoformat(), details, solution):
                    messagebox.showinfo("Success", "Service call logged successfully.")
                    service_dialog.destroy()
                    if hasattr(self, 'current_view') and self.current_view == "kanban":
                        self.populate_kanban_view()
                    else:
                        self.load_table_data()
                else:
                    messagebox.showerror("Error", "Failed to log service call.")
            else:
                messagebox.showerror("Error", "Please fill in both details and solution.")
        
        ctk.CTkButton(button_frame, text="Save", command=save_service_call).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=service_dialog.destroy).pack(side="left", padx=5)

    def renew_amc(self, amc):
        """Renew an expired AMC"""
        # Create renewal dialog
        renewal_dialog = ctk.CTkToplevel(self)
        renewal_dialog.title(f"Renew AMC #{amc[0]}")
        renewal_dialog.geometry("400x300")
        renewal_dialog.transient(self)
        renewal_dialog.grab_set()
        
        # Form fields
        form_frame = ctk.CTkFrame(renewal_dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(form_frame, text=f"Renewing AMC #{amc[0]} for {amc[1]}", font=ctk.CTkFont(weight="bold")).pack(pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="New Start Date:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 5))
        start_date_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        start_date_entry.insert(0, datetime.date.today().isoformat())
        start_date_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="New End Date:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        end_date_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        # Default to one year from today
        next_year = datetime.date.today() + datetime.timedelta(days=365)
        end_date_entry.insert(0, next_year.isoformat())
        end_date_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(form_frame, text="New Value (₹):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        value_entry = ctk.CTkEntry(form_frame, placeholder_text="0.00")
        value_entry.insert(0, str(amc[4]))  # Use previous value as default
        value_entry.pack(fill="x", pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        def save_renewal():
            try:
                start_date = start_date_entry.get()
                end_date = end_date_entry.get()
                value = float(value_entry.get())
                
                # Validate dates
                datetime.date.fromisoformat(start_date)
                datetime.date.fromisoformat(end_date)
                
                # Create new AMC (renewal)
                customer_id = None  # We need to get customer ID from customer name
                customers = db_manager.get_all_customers()
                customer = next((c for c in customers if c['name'] == amc[1]), None)
                if customer:
                    customer_id = customer['id']
                
                if customer_id and db_manager.add_amc(customer_id, start_date, end_date, value):
                    messagebox.showinfo("Success", f"AMC renewed successfully. New AMC created.")
                    renewal_dialog.destroy()
                    if hasattr(self, 'current_view') and self.current_view == "kanban":
                        self.populate_kanban_view()
                    else:
                        self.load_table_data()
                else:
                    messagebox.showerror("Error", "Failed to renew AMC.")
                    
            except (ValueError, TypeError):
                messagebox.showerror("Error", "Invalid date or value format.")
        
        ctk.CTkButton(button_frame, text="Renew", command=save_renewal).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=renewal_dialog.destroy).pack(side="left", padx=5)

    def show_add_amc_dialog(self):
        """Show dialog to add a new AMC"""
        # Switch to table view where the form is available
        self.show_table_view()

    def create_add_amc_form(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(parent, text="Add New AMC", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=4, pady=(0,5))
        ctk.CTkLabel(parent, text="Customer:").grid(row=1, column=0, padx=5, sticky="w")
        self.customer_combo = ctk.CTkComboBox(parent)
        self.customer_combo.grid(row=1, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(parent, text="Start Date:").grid(row=1, column=2, padx=5, sticky="w")
        self.start_date_entry = ctk.CTkEntry(parent, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=1, column=3, padx=5, sticky="ew")
        ctk.CTkLabel(parent, text="End Date:").grid(row=2, column=2, padx=5, sticky="w")
        self.end_date_entry = ctk.CTkEntry(parent, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=2, column=3, padx=5, sticky="ew")
        ctk.CTkLabel(parent, text="Value (₹):").grid(row=2, column=0, padx=5, sticky="w")
        self.value_entry = ctk.CTkEntry(parent, placeholder_text="0.00")
        self.value_entry.grid(row=2, column=1, padx=5, sticky="ew")
        ctk.CTkButton(parent, text="Save New AMC", command=self.add_amc).grid(row=2, column=4, padx=10)

    def load_table_data(self):
        """Load data for table view"""
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])
        self.load_amcs()
        self.clear_service_calls()
        self.add_service_call_button.configure(state="disabled")

    def load_data(self):
        """Public method to be called when switching to this frame"""
        if hasattr(self, 'current_view'):
            if self.current_view == "kanban":
                self.populate_kanban_view()
            else:
                self.load_table_data()
        else:
            # Default to kanban view
            self.populate_kanban_view()

    def load_amcs(self):
        for i in self.amc_tree.get_children(): self.amc_tree.delete(i)
        amcs = db_manager.get_all_amcs()
        for amc in amcs: self.amc_tree.insert("", "end", values=tuple(amc))

    def amc_selected(self, event=None):
        selected = self.amc_tree.focus()
        if not selected: return
        self.selected_amc_id = self.amc_tree.item(selected, "values")[0]
        self.service_label.configure(text=f"Service Calls for AMC #{self.selected_amc_id}")
        self.add_service_call_button.configure(state="normal")
        self.load_service_calls()

    def load_service_calls(self):
        self.clear_service_calls()
        if self.selected_amc_id:
            calls = db_manager.get_service_calls_for_amc(self.selected_amc_id)
            for call in calls: self.service_tree.insert("", "end", values=tuple(call))

    def clear_service_calls(self):
        for i in self.service_tree.get_children(): self.service_tree.delete(i)

    def add_amc(self):
        cust_name = self.customer_combo.get()
        customer = next((c for c in self.customers if c['name'] == cust_name), None)
        if not customer: return messagebox.showerror("Error", "Invalid customer.")
        try:
            value = float(self.value_entry.get())
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            datetime.date.fromisoformat(start_date); datetime.date.fromisoformat(end_date)
        except: return messagebox.showerror("Error", "Invalid date or value format.")

        if db_manager.add_amc(customer['id'], start_date, end_date, value):
            messagebox.showinfo("Success", "AMC created.")
            self.load_amcs()
        else: messagebox.showerror("Error", "Failed to create AMC.")

    def add_service_call(self):
        if not self.selected_amc_id: return
        details = simpledialog.askstring("Input", "Enter service details:", parent=self)
        solution = simpledialog.askstring("Input", "Enter solution offered:", parent=self)
        if details and solution:
            if db_manager.add_amc_service_call(self.selected_amc_id, datetime.date.today().isoformat(), details, solution):
                messagebox.showinfo("Success", "Service call logged.")
                self.load_service_calls()
            else: messagebox.showerror("Error", "Failed to log service call.")
