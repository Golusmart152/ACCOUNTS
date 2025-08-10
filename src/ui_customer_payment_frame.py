import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager
from . import db_manager
from .ui_payment_allocation_dialog import PaymentAllocationDialog
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CustomerPaymentFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Receive Customer Payment", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Header ---
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.customer_combo = ctk.CTkComboBox(header_frame, command=self.customer_selected)
        self.customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Payment Amount:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = ctk.CTkEntry(header_frame, placeholder_text="0.00")
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Payment Date:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.date_entry = ctk.CTkEntry(header_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # --- Invoices Table ---
        invoices_frame = ctk.CTkFrame(self)
        invoices_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        invoices_frame.grid_columnconfigure(0, weight=1)
        invoices_frame.grid_rowconfigure(0, weight=1)

        columns = ("invoice_id", "date", "status", "total", "due")
        self.tree = ttk.Treeview(invoices_frame, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.replace('_', ' ').title())
        self.tree.grid(row=0, column=0, sticky="nsew")

        # --- Footer ---
        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.save_button = ctk.CTkButton(footer_frame, text="Allocate and Save Payment", command=self.save_payment)
        self.save_button.pack()

    def load_data(self):
        """Called when the frame is shown."""
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])
        if self.customers:
            self.customer_combo.set(self.customers[0]['name'])
            self.customer_selected(self.customers[0]['name'])
        else:
            self.customer_combo.set("")
            self.clear_invoice_tree()
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.date.today().isoformat())

    def customer_selected(self, customer_name):
        customer = next((c for c in self.customers if c['name'] == customer_name), None)
        if customer:
            self.clear_invoice_tree()
            invoices = db_manager.get_unpaid_sales_invoices(customer['id'])
            for inv in invoices:
                due_amount = inv['total_amount'] - inv['amount_paid']
                self.tree.insert("", "end", values=(inv['id'], inv['invoice_date'], inv['status'], f"{inv['total_amount']:.2f}", f"{due_amount:.2f}"), iid=inv['id'])

    def clear_invoice_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def save_payment(self):
        customer_name = self.customer_combo.get()
        amount_str = self.amount_entry.get()
        payment_date = self.date_entry.get()

        if not all([customer_name, amount_str, payment_date]):
            return messagebox.showerror("Error", "Customer, Payment Amount, and Date are required.")

        try:
            payment_amount = float(amount_str)
            if payment_amount <= 0: raise ValueError()
        except ValueError:
            return messagebox.showerror("Error", "Payment amount must be a positive number.")

        customer = next((c for c in self.customers if c['name'] == customer_name), None)
        if not customer: return messagebox.showerror("Error", "Invalid customer.")

        invoices_to_pay = db_manager.get_unpaid_sales_invoices(customer['id'])
        if not invoices_to_pay:
            return messagebox.showinfo("No Invoices", "This customer has no unpaid invoices.")

        dialog = PaymentAllocationDialog(self, invoices_to_pay, payment_amount)
        allocations = dialog.get_allocations()

        if not allocations:
            return # User cancelled or allocated nothing

        # Final validation and save
        payment_id = db_manager.record_customer_payment(customer['id'], payment_date, payment_amount, allocations)

        if payment_id:
            messagebox.showinfo("Success", f"Payment recorded with ID: {payment_id}")
            self.load_data() # Refresh everything
        else:
            messagebox.showerror("Error", "Failed to record payment. Check logs for details.")
