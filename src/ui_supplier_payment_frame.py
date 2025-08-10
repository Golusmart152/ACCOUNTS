import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
from ui_payment_allocation_dialog import PaymentAllocationDialog
import datetime

# Xero Color Scheme
XERO_BLUE = "#13B5EA"
XERO_NAVY = "#1E3A8A"
XERO_WHITE = "#FFFFFF"
XERO_LIGHT_GRAY = "#F9FAFB"
XERO_GRAY = "#6B7280"
XERO_DARK_GRAY = "#374151"
XERO_GREEN = "#10B981"
XERO_RED = "#EF4444"
XERO_ORANGE = "#F59E0B"

class SupplierPaymentFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container with Xero styling
        main_container = ctk.CTkFrame(self, fg_color=XERO_WHITE, corner_radius=12)
        main_container.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1)
        
        # Xero-style header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=25, pady=25, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Main title with Xero typography
        ctk.CTkLabel(header_frame, text="Make Supplier Payment",
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, sticky="w")
        
        # Quick action button
        quick_pay_button = ctk.CTkButton(header_frame, text="💳 Quick Payment",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=XERO_ORANGE, hover_color="#D97706",
                                        corner_radius=8, height=40, width=150,
                                        command=self.quick_payment_dialog)
        quick_pay_button.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        # Payment form section
        form_container = ctk.CTkFrame(main_container, fg_color=XERO_WHITE, corner_radius=12)
        form_container.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="ew")
        form_container.grid_columnconfigure((1, 3), weight=1)
        
        # Form title
        ctk.CTkLabel(form_container, text="Payment Details",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, columnspan=4,
                                              padx=25, pady=(25, 20), sticky="w")
        
        # Form fields with Xero styling
        ctk.CTkLabel(form_container, text="Supplier",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=0, padx=(25, 10), pady=8, sticky="w")
        self.supplier_combo = ctk.CTkComboBox(form_container, values=[],
                                             font=ctk.CTkFont(size=14),
                                             height=40, corner_radius=8,
                                             command=self.supplier_selected)
        self.supplier_combo.grid(row=1, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Payment Amount",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        self.amount_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                        height=40, corner_radius=8, border_color=XERO_GRAY,
                                        placeholder_text="₹0.00")
        self.amount_entry.grid(row=1, column=3, padx=(0, 25), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Payment Date",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, padx=(25, 10), pady=8, sticky="w")
        self.date_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                      height=40, corner_radius=8, border_color=XERO_GRAY,
                                      placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=2, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Payment Method",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=2, padx=(0, 10), pady=8, sticky="w")
        self.payment_method_combo = ctk.CTkComboBox(form_container, 
                                                   values=["Bank Transfer", "Cheque", "Cash", "UPI", "RTGS/NEFT"],
                                                   font=ctk.CTkFont(size=14),
                                                   height=40, corner_radius=8)
        self.payment_method_combo.grid(row=2, column=3, padx=(0, 25), pady=8, sticky="ew")
        self.payment_method_combo.set("Bank Transfer")
        
        # Reference number field
        ctk.CTkLabel(form_container, text="Reference Number",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=3, column=0, padx=(25, 10), pady=8, sticky="w")
        self.reference_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                           height=40, corner_radius=8, border_color=XERO_GRAY,
                                           placeholder_text="Transaction/Cheque Number")
        self.reference_entry.grid(row=3, column=1, padx=(0, 20), pady=(8, 25), sticky="ew")
        
        # Outstanding invoices section
        invoices_container = ctk.CTkFrame(main_container, fg_color=XERO_WHITE, corner_radius=12)
        invoices_container.grid(row=2, column=0, padx=25, pady=(0, 25), sticky="nsew")
        invoices_container.grid_columnconfigure(0, weight=1)
        invoices_container.grid_rowconfigure(1, weight=1)
        
        # Section title with summary
        title_frame = ctk.CTkFrame(invoices_container, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=25, pady=(25, 15), sticky="ew")
        title_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(title_frame, text="Outstanding Purchase Invoices",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, sticky="w")
        
        self.outstanding_summary = ctk.CTkLabel(title_frame, text="Total Outstanding: ₹0.00",
                                               font=ctk.CTkFont(size=14, weight="bold"),
                                               text_color=XERO_RED)
        self.outstanding_summary.grid(row=0, column=1, sticky="e")
        
        # Invoices table with modern styling
        table_frame = ctk.CTkFrame(invoices_container, fg_color="transparent")
        table_frame.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("invoice_id", "date", "status", "total", "paid", "due")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Configure column headings
        self.tree.heading("invoice_id", text="Purchase Order #")
        self.tree.heading("date", text="Date")
        self.tree.heading("status", text="Status")
        self.tree.heading("total", text="Total Amount")
        self.tree.heading("paid", text="Amount Paid")
        self.tree.heading("due", text="Amount Due")
        
        # Configure column widths
        self.tree.column("invoice_id", width=120, anchor="center")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("paid", width=120, anchor="e")
        self.tree.column("due", width=120, anchor="e")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Action buttons with Xero styling
        button_frame = ctk.CTkFrame(invoices_container, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=25, pady=(0, 25), sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Payment summary
        summary_frame = ctk.CTkFrame(button_frame, fg_color=XERO_ORANGE, corner_radius=8)
        summary_frame.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        self.payment_summary = ctk.CTkLabel(summary_frame, text="Payment Amount: ₹0.00",
                                           font=ctk.CTkFont(size=16, weight="bold"),
                                           text_color=XERO_WHITE)
        self.payment_summary.pack(padx=20, pady=12)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        actions_frame.grid(row=1, column=0, sticky="e")
        
        clear_button = ctk.CTkButton(actions_frame, text="Clear Form",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                    text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                    corner_radius=8, height=40, width=120,
                                    command=self.clear_form)
        clear_button.pack(side="right", padx=5)
        
        self.save_button = ctk.CTkButton(actions_frame, text="💳 Allocate & Save Payment",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=XERO_ORANGE, hover_color="#D97706",
                                        corner_radius=8, height=40, width=200,
                                        command=self.save_payment)
        self.save_button.pack(side="right", padx=5)
        
        # Bind amount entry to update summary
        self.amount_entry.bind("<KeyRelease>", self.update_payment_summary)

    def quick_payment_dialog(self):
        """Show quick payment dialog for common amounts"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Quick Payment")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=XERO_LIGHT_GRAY)
        
        # Dialog content
        content = ctk.CTkFrame(dialog, fg_color=XERO_WHITE, corner_radius=12)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content, text="Quick Payment Amounts",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).pack(pady=(20, 15))
        
        # Quick amount buttons
        amounts = [5000, 10000, 25000, 50000, 100000]
        for amount in amounts:
            btn = ctk.CTkButton(content, text=f"₹{amount:,}",
                               font=ctk.CTkFont(size=14, weight="bold"),
                               fg_color=XERO_ORANGE, hover_color="#D97706",
                               corner_radius=8, height=40,
                               command=lambda a=amount: self.set_quick_amount(a, dialog))
            btn.pack(fill="x", padx=20, pady=5)
        
        # Cancel button
        ctk.CTkButton(content, text="Cancel",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                     text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                     corner_radius=8, height=40,
                     command=dialog.destroy).pack(fill="x", padx=20, pady=(10, 20))

    def set_quick_amount(self, amount, dialog):
        """Set quick payment amount and close dialog"""
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(amount))
        self.update_payment_summary()
        dialog.destroy()

    def update_payment_summary(self, event=None):
        """Update payment summary display"""
        try:
            amount = float(self.amount_entry.get() or 0)
            self.payment_summary.configure(text=f"Payment Amount: ₹{amount:,.2f}")
        except ValueError:
            self.payment_summary.configure(text="Payment Amount: ₹0.00")

    def load_data(self):
        """Called when the frame is shown"""
        self.suppliers = db_manager.get_all_suppliers()
        self.supplier_combo.configure(values=[s['name'] for s in self.suppliers])
        if self.suppliers:
            self.supplier_combo.set(self.suppliers[0]['name'])
            self.supplier_selected(self.suppliers[0]['name'])
        else:
            self.supplier_combo.set("")
            self.clear_invoice_tree()
        
        # Reset form
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.payment_method_combo.set("Bank Transfer")
        self.reference_entry.delete(0, "end")
        self.update_payment_summary()

    def supplier_selected(self, supplier_name):
        """Handle supplier selection"""
        supplier = next((s for s in self.suppliers if s['name'] == supplier_name), None)
        if supplier:
            self.clear_invoice_tree()
            invoices = db_manager.get_unpaid_purchase_invoices(supplier['id'])
            total_outstanding = 0
            
            for inv in invoices:
                due_amount = inv['total_amount'] - inv['amount_paid']
                total_outstanding += due_amount
                self.tree.insert("", "end", values=(
                    f"PO-{inv['id']:04d}",
                    inv['invoice_date'],
                    inv['status'],
                    f"₹{inv['total_amount']:,.2f}",
                    f"₹{inv['amount_paid']:,.2f}",
                    f"₹{due_amount:,.2f}"
                ), iid=inv['id'])
            
            # Update outstanding summary
            self.outstanding_summary.configure(text=f"Total Outstanding: ₹{total_outstanding:,.2f}")
        else:
            self.clear_invoice_tree()

    def clear_invoice_tree(self):
        """Clear the invoice tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.outstanding_summary.configure(text="Total Outstanding: ₹0.00")

    def clear_form(self):
        """Clear the payment form"""
        self.amount_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.payment_method_combo.set("Bank Transfer")
        self.reference_entry.delete(0, "end")
        self.update_payment_summary()

    def save_payment(self):
        """Save the supplier payment"""
        supplier_name = self.supplier_combo.get()
        amount_str = self.amount_entry.get()
        payment_date = self.date_entry.get()
        payment_method = self.payment_method_combo.get()
        reference = self.reference_entry.get()

        if not all([supplier_name, amount_str, payment_date]):
            return messagebox.showerror("Validation Error", "Supplier, Payment Amount, and Date are required.")

        try:
            payment_amount = float(amount_str)
            if payment_amount <= 0:
                raise ValueError()
        except ValueError:
            return messagebox.showerror("Validation Error", "Payment amount must be a positive number.")

        supplier = next((s for s in self.suppliers if s['name'] == supplier_name), None)
        if not supplier:
            return messagebox.showerror("Error", "Invalid supplier selected.")

        invoices_to_pay = db_manager.get_unpaid_purchase_invoices(supplier['id'])
        if not invoices_to_pay:
            return messagebox.showinfo("No Outstanding Invoices", "This supplier has no unpaid invoices.")

        # Open payment allocation dialog
        dialog = PaymentAllocationDialog(self, invoices_to_pay, payment_amount)
        allocations = dialog.get_allocations()

        if not allocations:
            return  # User cancelled or allocated nothing

        # Save payment with allocations
        payment_id = db_manager.record_supplier_payment(supplier['id'], payment_date, payment_amount, allocations)

        if payment_id:
            messagebox.showinfo("Payment Recorded", f"Supplier payment successfully recorded with ID: {payment_id}")
            self.load_data()  # Refresh the form
        else:
            messagebox.showerror("Error", "Failed to record payment. Please check the logs for details.")
