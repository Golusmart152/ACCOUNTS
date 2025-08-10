import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from . import db_manager
from . import pdf_generator
from .pdf_generator import generate_job_sheet_pdf
import os

class JobSheetFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(header_frame, text="Job Sheet / RMA Management", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="Create New Job Sheet", command=self.open_new_job_sheet_window).pack(side="right")

        # --- Job Sheet List ---
        self.tree = ttk.Treeview(self, columns=("id", "date", "customer", "product", "status"), show="headings")
        for col in ("id", "date", "customer", "product", "status"): self.tree.heading(col, text=col.title())
        self.tree.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.job_sheet_selected)

        # --- Details & Actions Panel ---
        details_frame = ctk.CTkFrame(self)
        details_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.details_label = ctk.CTkLabel(details_frame, text="Select a job sheet to see details.", justify="left")
        self.details_label.pack(side="left", anchor="w", padx=5)

        self.update_status_button = ctk.CTkButton(details_frame, text="Update Status", state="disabled", command=self.update_status)
        self.update_status_button.pack(side="right", padx=5)
        self.print_pdf_button = ctk.CTkButton(details_frame, text="Print Slip", state="disabled", command=self.print_slip)
        self.print_pdf_button.pack(side="right", padx=5)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        sheets = db_manager.get_all_job_sheets()
        for sheet in sheets:
            self.tree.insert("", "end", values=(sheet['id'], sheet['received_date'], sheet['customer_name'], sheet['product_name'], sheet['status']), iid=sheet['id'])
        self.details_label.configure(text="Select a job sheet to see details.")
        self.update_status_button.configure(state="disabled")
        self.print_pdf_button.configure(state="disabled")

    def job_sheet_selected(self, event=None):
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
        selected = self.tree.focus()
        if not selected: return
        sheet_id = self.tree.item(selected, "values")[0]

        statuses = ['Received', 'Under Diagnosis', 'Awaiting Parts', 'Assigned to 3rd Party', 'Ready for Collection', 'Delivered']
        new_status = simpledialog.askstring("Update Status", "Enter new status:", initialvalue=self.tree.item(selected, "values")[4], parent=self)

        if new_status and new_status in statuses:
            if db_manager.update_job_sheet_status(sheet_id, new_status):
                messagebox.showinfo("Success", "Status updated.")
                self.load_data()
            else: messagebox.showerror("Error", "Failed to update status.")
        elif new_status:
            messagebox.showwarning("Invalid Status", f"Please use one of: {', '.join(statuses)}")

    def print_slip(self):
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
        NewJobSheetWindow(self)

class NewJobSheetWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Create New Job Sheet")
        self.geometry("600x500")

        self.grid_columnconfigure(1, weight=1)
        # ... (Full implementation of the form)

        self.create_form_widgets()
        self.load_customers()

    def create_form_widgets(self):
        # Customer, Product, Serial, Problem, Accessories, etc.
        # This is a simplified placeholder
        ctk.CTkLabel(self, text="Customer:").grid(row=0, column=0, padx=10, pady=5)
        self.customer_combo = ctk.CTkComboBox(self, values=[])
        self.customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Product Name:").grid(row=1, column=0, padx=10, pady=5)
        self.product_entry = ctk.CTkEntry(self)
        self.product_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Accessories (comma-separated):").grid(row=2, column=0, padx=10, pady=5)
        self.accessories_entry = ctk.CTkEntry(self)
        self.accessories_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(self, text="Save Job Sheet", command=self.save).grid(row=3, column=1, pady=10)

    def load_customers(self):
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])

    def save(self):
        # Get all data from form
        # Call db_manager.add_job_sheet
        # Close window and refresh parent
        cust_name = self.customer_combo.get()
        customer = next((c for c in self.customers if c['name'] == cust_name), None)
        if not customer: return messagebox.showerror("Error", "Invalid customer.")

        data = {
            "customer_id": customer['id'],
            "received_date": datetime.date.today().isoformat(),
            "product_name": self.product_entry.get(),
            "product_serial": "N/A", # Simplified
            "reported_problem": "N/A",
            "estimated_cost": 0.0,
            "estimated_timeline": "N/A",
            "assigned_to": ""
        }
        accessories = [acc.strip() for acc in self.accessories_entry.get().split(',') if acc.strip()]

        job_id = db_manager.add_job_sheet(data, accessories)
        if job_id:
            messagebox.showinfo("Success", f"Job Sheet #{job_id} created.")
            self.parent.load_data()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to create job sheet.")
