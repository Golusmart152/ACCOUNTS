import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import db_manager
import pdf_generator
from pdf_generator import generate_job_sheet_pdf
import os
import datetime

class JobSheetFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with title and view toggle
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="Job Sheet / RMA Management", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # View toggle buttons
        view_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        view_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        self.kanban_view_button = ctk.CTkButton(view_frame, text="Kanban View", command=self.show_kanban_view)
        self.kanban_view_button.pack(side="left", padx=5)
        
        self.table_view_button = ctk.CTkButton(view_frame, text="Table View", command=self.show_table_view)
        self.table_view_button.pack(side="left", padx=5)
        
        ctk.CTkButton(view_frame, text="Create New Job Sheet", command=self.open_new_job_sheet_window).pack(side="left", padx=5)

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
        """Create a Kanban board for managing job sheets"""
        self.kanban_view_frame = ctk.CTkFrame(parent)
        self.kanban_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.kanban_view_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.kanban_view_frame.grid_rowconfigure(0, weight=1)
        
        # Kanban columns for different job sheet statuses
        self.statuses = ["Received", "Under Diagnosis", "Awaiting Parts", "Assigned to 3rd Party", "Ready for Collection", "Delivered"]
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
            
            # Scrollable content area for job sheet cards
            content_frame = ctk.CTkScrollableFrame(column_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            content_frame.grid_columnconfigure(0, weight=1)
            
            self.kanban_columns[status] = content_frame
            
        # Load job sheets into kanban
        self.populate_kanban_view()
        
    def create_table_view(self, parent):
        """Create the traditional table view for job sheets"""
        self.table_view_frame = ctk.CTkFrame(parent)
        self.table_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.table_view_frame.grid_columnconfigure(0, weight=1)
        self.table_view_frame.grid_rowconfigure(1, weight=1)

        # Job Sheet List
        self.tree = ttk.Treeview(self.table_view_frame, columns=("id", "date", "customer", "product", "status"), show="headings")
        for col in ("id", "date", "customer", "product", "status"): 
            self.tree.heading(col, text=col.title())
        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.job_sheet_selected)

        # Details & Actions Panel
        details_frame = ctk.CTkFrame(self.table_view_frame)
        details_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.details_label = ctk.CTkLabel(details_frame, text="Select a job sheet to see details.", justify="left")
        self.details_label.pack(side="left", anchor="w", padx=5)

        self.update_status_button = ctk.CTkButton(details_frame, text="Update Status", state="disabled", command=self.update_status)
        self.update_status_button.pack(side="right", padx=5)
        self.print_pdf_button = ctk.CTkButton(details_frame, text="Print Slip", state="disabled", command=self.print_slip)
        self.print_pdf_button.pack(side="right", padx=5)

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
        """Populate the Kanban view with job sheets from database"""
        # Clear existing cards
        for status in self.kanban_columns:
            for widget in self.kanban_columns[status].winfo_children():
                widget.destroy()
                
        # Get job sheets from database
        sheets = db_manager.get_all_job_sheets()
        
        for sheet in sheets:
            self.add_job_sheet_to_kanban(sheet)
            
    def add_job_sheet_to_kanban(self, sheet):
        """Add a job sheet card to the appropriate Kanban column"""
        status = sheet["status"]
        if status in self.kanban_columns:
            card_frame = ctk.CTkFrame(self.kanban_columns[status], corner_radius=8)
            card_frame.pack(fill="x", padx=5, pady=5)
            card_frame.grid_columnconfigure(0, weight=1)
            
            # Job sheet header
            header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(10, 5))
            header_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(header_frame, text=f"Job #{sheet['id']}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(header_frame, text=sheet['received_date'], font=ctk.CTkFont(size=10)).grid(row=0, column=1, sticky="e")
            
            # Job sheet details
            ctk.CTkLabel(card_frame, text=f"Customer: {sheet['customer_name']}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=2)
            ctk.CTkLabel(card_frame, text=f"Product: {sheet['product_name']}", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=2)
            
            # Truncate problem description if too long
            problem = sheet['reported_problem'] or "No problem description"
            if len(problem) > 40:
                problem = problem[:40] + "..."
            ctk.CTkLabel(card_frame, text=f"Issue: {problem}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=2)
            
            # Assigned to and cost
            if sheet['assigned_to']:
                ctk.CTkLabel(card_frame, text=f"Assigned: {sheet['assigned_to']}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=2)
            
            if sheet['estimated_cost'] and sheet['estimated_cost'] > 0:
                ctk.CTkLabel(card_frame, text=f"Est. Cost: ₹{sheet['estimated_cost']:.2f}", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=2)
            
            # Action buttons
            button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            # Move to next status button
            next_status = self.get_next_status(status)
            if next_status:
                ctk.CTkButton(button_frame, text=f"→ {next_status}", width=80, height=25, font=ctk.CTkFont(size=10),
                             command=lambda s=sheet, ns=next_status: self.move_job_sheet(s, ns)).pack(side="left", padx=2)
            
            ctk.CTkButton(button_frame, text="Details", width=60, height=25, font=ctk.CTkFont(size=10),
                         command=lambda s=sheet: self.show_job_sheet_details(s)).pack(side="left", padx=2)
            ctk.CTkButton(button_frame, text="Print", width=50, height=25, font=ctk.CTkFont(size=10),
                         command=lambda s=sheet: self.print_job_sheet_slip(s)).pack(side="left", padx=2)

    def get_next_status(self, current_status):
        """Get the next status in the workflow"""
        try:
            current_index = self.statuses.index(current_status)
            if current_index < len(self.statuses) - 1:
                return self.statuses[current_index + 1]
        except ValueError:
            pass
        return None

    def move_job_sheet(self, sheet, new_status):
        """Move a job sheet to a new status"""
        if db_manager.update_job_sheet_status(sheet['id'], new_status):
            messagebox.showinfo("Success", f"Job Sheet #{sheet['id']} moved to '{new_status}'")
            self.populate_kanban_view()
        else:
            messagebox.showerror("Error", "Failed to update job sheet status.")

    def show_job_sheet_details(self, sheet):
        """Show detailed information about a job sheet"""
        sheet_details, accessories = db_manager.get_job_sheet_details(sheet['id'])
        
        # Create details dialog
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Job Sheet #{sheet['id']} Details")
        details_window.geometry("500x400")
        details_window.transient(self)
        details_window.grab_set()
        
        # Details content
        details_frame = ctk.CTkScrollableFrame(details_window)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        details_text = f"""
Job ID: {sheet_details['id']}
Status: {sheet_details['status']}
Customer: {sheet_details['customer_name']}
Product: {sheet_details['product_name']}
Serial Number: {sheet_details['product_serial']}
Received Date: {sheet_details['received_date']}
Problem: {sheet_details['reported_problem']}
Assigned To: {sheet_details['assigned_to'] or 'N/A'}
Estimated Cost: ₹{sheet_details['estimated_cost']:.2f}
Estimated Timeline: {sheet_details['estimated_timeline']}
Accessories: {', '.join([a['name'] for a in accessories]) if accessories else 'None'}
        """
        
        ctk.CTkLabel(details_frame, text=details_text.strip(), justify="left", font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        # Action buttons
        button_frame = ctk.CTkFrame(details_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(button_frame, text="Update Status", command=lambda: self.update_job_status_dialog(sheet)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Print Slip", command=lambda: self.print_job_sheet_slip(sheet)).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Close", command=details_window.destroy).pack(side="right", padx=5)

    def update_job_status_dialog(self, sheet):
        """Show dialog to update job sheet status"""
        new_status = simpledialog.askstring("Update Status", 
                                           f"Current status: {sheet['status']}\n\nSelect new status:",
                                           initialvalue=sheet['status'], parent=self)
        
        if new_status and new_status in self.statuses:
            if db_manager.update_job_sheet_status(sheet['id'], new_status):
                messagebox.showinfo("Success", "Status updated successfully.")
                if hasattr(self, 'current_view') and self.current_view == "kanban":
                    self.populate_kanban_view()
                else:
                    self.load_table_data()
            else:
                messagebox.showerror("Error", "Failed to update status.")
        elif new_status:
            messagebox.showwarning("Invalid Status", f"Please use one of: {', '.join(self.statuses)}")

    def print_job_sheet_slip(self, sheet):
        """Print job sheet slip"""
        sheet_details, accessories = db_manager.get_job_sheet_details(sheet['id'])
        
        pdf_data = dict(sheet_details)
        pdf_data['accessories'] = [a['name'] for a in accessories]

        # Create a 'job_slips' directory if it doesn't exist
        if not os.path.exists("job_slips"):
            os.makedirs("job_slips")

        filename = f"job_slips/Job_Sheet_{sheet['id']}.pdf"
        generate_job_sheet_pdf(filename, pdf_data)
        messagebox.showinfo("Success", f"PDF slip generated: {filename}")

    def load_table_data(self):
        """Load data for table view"""
        for i in self.tree.get_children(): 
            self.tree.delete(i)
        sheets = db_manager.get_all_job_sheets()
        for sheet in sheets:
            self.tree.insert("", "end", values=(sheet['id'], sheet['received_date'], sheet['customer_name'], sheet['product_name'], sheet['status']), iid=sheet['id'])
        self.details_label.configure(text="Select a job sheet to see details.")
        self.update_status_button.configure(state="disabled")
        self.print_pdf_button.configure(state="disabled")

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

    def job_sheet_selected(self, event=None):
        """Handle job sheet selection in table view"""
        selected = self.tree.focus()
        if not selected: return

        sheet_id = self.tree.item(selected, "values")[0]
        sheet, accessories = db_manager.get_job_sheet_details(sheet_id)

        acc_list = [a['name'] for a in accessories]
        details_text = f"""
Job ID: {sheet['id']}  |  Status: {sheet['status']}
Customer: {sheet['customer_name']}
Product: {sheet['product_name']} (SN: {sheet['product_serial']})
Problem: {sheet['reported_problem']}
Accessories: {', '.join(acc_list) if acc_list else 'None'}
Assigned To: {sheet['assigned_to'] or 'N/A'}
Est. Cost: {sheet['estimated_cost']:.2f} | Est. Timeline: {sheet['estimated_timeline']}
        """
        self.details_label.configure(text=details_text.strip())
        self.update_status_button.configure(state="normal")
        self.print_pdf_button.configure(state="normal")

    def update_status(self):
        """Update status from table view"""
        selected = self.tree.focus()
        if not selected: return
        sheet_id = self.tree.item(selected, "values")[0]

        new_status = simpledialog.askstring("Update Status", "Enter new status:", initialvalue=self.tree.item(selected, "values")[4], parent=self)

        if new_status and new_status in self.statuses:
            if db_manager.update_job_sheet_status(sheet_id, new_status):
                messagebox.showinfo("Success", "Status updated.")
                self.load_table_data()
            else: 
                messagebox.showerror("Error", "Failed to update status.")
        elif new_status:
            messagebox.showwarning("Invalid Status", f"Please use one of: {', '.join(self.statuses)}")

    def print_slip(self):
        """Print slip from table view"""
        selected = self.tree.focus()
        if not selected: return
        sheet_id = self.tree.item(selected, "values")[0]
        sheet, accessories = db_manager.get_job_sheet_details(sheet_id)

        pdf_data = dict(sheet)
        pdf_data['accessories'] = [a['name'] for a in accessories]

        # Create a 'job_slips' directory if it doesn't exist
        if not os.path.exists("job_slips"):
            os.makedirs("job_slips")

        filename = f"job_slips/Job_Sheet_{sheet_id}.pdf"
        generate_job_sheet_pdf(filename, pdf_data)
        messagebox.showinfo("Success", f"PDF slip generated: {filename}")

    def open_new_job_sheet_window(self):
        """Open window to create new job sheet"""
        NewJobSheetWindow(self)

class NewJobSheetWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Create New Job Sheet")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(1, weight=1)
        self.create_form_widgets()
        self.load_customers()

    def create_form_widgets(self):
        # Customer, Product, Serial, Problem, Accessories, etc.
        ctk.CTkLabel(self, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.customer_combo = ctk.CTkComboBox(self, values=[])
        self.customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Product Name:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.product_entry = ctk.CTkEntry(self)
        self.product_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Product Serial:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.serial_entry = ctk.CTkEntry(self)
        self.serial_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Reported Problem:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.problem_entry = ctk.CTkTextbox(self, height=80)
        self.problem_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Accessories (comma-separated):").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.accessories_entry = ctk.CTkEntry(self)
        self.accessories_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Assigned To:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.assigned_entry = ctk.CTkEntry(self)
        self.assigned_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Estimated Cost:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.cost_entry = ctk.CTkEntry(self, placeholder_text="0.00")
        self.cost_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Estimated Timeline:").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.timeline_entry = ctk.CTkEntry(self, placeholder_text="e.g., 3-5 days")
        self.timeline_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(button_frame, text="Save Job Sheet", command=self.save).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

    def load_customers(self):
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])

    def save(self):
        # Get all data from form
        cust_name = self.customer_combo.get()
        customer = next((c for c in self.customers if c['name'] == cust_name), None)
        if not customer: 
            return messagebox.showerror("Error", "Please select a valid customer.")

        try:
            estimated_cost = float(self.cost_entry.get() or 0.0)
        except ValueError:
            return messagebox.showerror("Error", "Invalid cost format.")

        data = {
            "customer_id": customer['id'],
            "received_date": datetime.date.today().isoformat(),
            "product_name": self.product_entry.get().strip(),
            "product_serial": self.serial_entry.get().strip() or "N/A",
            "reported_problem": self.problem_entry.get("1.0", "end-1c").strip() or "N/A",
            "estimated_cost": estimated_cost,
            "estimated_timeline": self.timeline_entry.get().strip() or "N/A",
            "assigned_to": self.assigned_entry.get().strip()
        }
        
        accessories = [acc.strip() for acc in self.accessories_entry.get().split(',') if acc.strip()]

        job_id = db_manager.add_job_sheet(data, accessories)
        if job_id:
            messagebox.showinfo("Success", f"Job Sheet #{job_id} created successfully.")
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to create job sheet.")
