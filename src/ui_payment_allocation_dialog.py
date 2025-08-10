import customtkinter as ctk
from tkinter import messagebox

class PaymentAllocationDialog(ctk.CTkToplevel):
    def __init__(self, parent, invoices, payment_amount):
        super().__init__(parent)
        self.transient(parent)
        self.title("Allocate Payment")
        self.geometry("500x400")

        self.invoices = invoices
        self.payment_amount = payment_amount
        self._allocations = []
        self.entries = {}

        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(header_frame, text=f"Total Payment: {payment_amount:.2f}").pack(side="left")
        self.unallocated_label = ctk.CTkLabel(header_frame, text=f"Unallocated: {payment_amount:.2f}", font=ctk.CTkFont(weight="bold"))
        self.unallocated_label.pack(side="right")

        # --- Invoices Frame ---
        invoices_frame = ctk.CTkScrollableFrame(self)
        invoices_frame.pack(pady=10, padx=10, fill="both", expand=True)

        for i, inv in enumerate(self.invoices):
            due = inv['total_amount'] - inv['amount_paid']
            row_frame = ctk.CTkFrame(invoices_frame)
            row_frame.pack(fill="x", pady=2)

            label_text = f"Inv #{inv['invoice_number']} ({inv['invoice_date']}) - Due: {due:.2f}"
            ctk.CTkLabel(row_frame, text=label_text).pack(side="left", padx=5)

            entry = ctk.CTkEntry(row_frame, placeholder_text="0.00", width=100)
            entry.pack(side="right", padx=5)
            entry.bind("<KeyRelease>", self.update_unallocated)
            self.entries[inv['id']] = entry

        # --- Buttons ---
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        self.ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok).pack(side="left", padx=10)
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel).pack(side="left", padx=10)

        self.grab_set()
        self.wait_window()

    def update_unallocated(self, event=None):
        total_allocated = 0
        for inv_id, entry in self.entries.items():
            try:
                total_allocated += float(entry.get() or 0)
            except ValueError:
                pass
        unallocated = self.payment_amount - total_allocated
        self.unallocated_label.configure(text=f"Unallocated: {unallocated:.2f}")

    def on_ok(self):
        total_allocated = 0
        temp_allocations = []
        for inv_id, entry in self.entries.items():
            try:
                amount = float(entry.get() or 0)
                if amount > 0:
                    invoice = next(inv for inv in self.invoices if inv['id'] == inv_id)
                    due = invoice['total_amount'] - invoice['amount_paid']
                    if amount > due + 0.001: # Add tolerance for float issues
                        messagebox.showerror("Error", f"Cannot apply {amount:.2f} to Invoice #{invoice['invoice_number']}. Amount due is {due:.2f}.", parent=self)
                        return
                    total_allocated += amount
                    temp_allocations.append((inv_id, amount))
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for allocation.", parent=self)
                return

        if total_allocated > self.payment_amount + 0.001:
            messagebox.showerror("Error", f"Total allocated amount ({total_allocated:.2f}) cannot exceed the payment amount ({self.payment_amount:.2f}).", parent=self)
            return

        self._allocations = temp_allocations
        self.destroy()

    def on_cancel(self):
        self._allocations = []
        self.destroy()

    def get_allocations(self):
        return self._allocations
