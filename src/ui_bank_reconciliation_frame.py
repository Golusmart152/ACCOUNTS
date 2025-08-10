import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import datetime

class BankReconciliationFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Bank Reconciliation", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Main Frame ---
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # --- Treeview for unreconciled transactions ---
        columns = ("id", "date", "description", "debit", "credit")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", selectmode="extended")
        for col in columns: self.tree.heading(col, text=col.title())
        self.tree.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # --- Action Panel ---
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(action_frame, text="Reconciliation Date:").pack(side="left", padx=10)
        self.recon_date_entry = ctk.CTkEntry(action_frame, placeholder_text="YYYY-MM-DD")
        self.recon_date_entry.insert(0, datetime.date.today().isoformat())
        self.recon_date_entry.pack(side="left", padx=5)

        self.reconcile_button = ctk.CTkButton(action_frame, text="Mark Selected as Reconciled", command=self.reconcile_selected)
        self.reconcile_button.pack(side="left", padx=20)

        # --- Quick Transaction ---
        quick_tran_frame = ctk.CTkFrame(self)
        quick_tran_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(quick_tran_frame, text="Quick Transaction (e.g., Bank Fees):").pack(side="left", padx=10)
        # Simplified: A full implementation would be here.

    def load_data(self):
        """Called when the frame is shown."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        transactions = db_manager.get_unreconciled_cash_transactions()

        for tran in transactions:
            debit = f"{tran['debit']:.2f}" if tran['debit'] else ""
            credit = f"{tran['credit']:.2f}" if tran['credit'] else ""
            self.tree.insert("", "end", values=(tran['id'], tran['date'], tran['description'], debit, credit))

    def reconcile_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return messagebox.showwarning("Warning", "No transactions selected.")

        recon_date = self.recon_date_entry.get()
        try:
            datetime.date.fromisoformat(recon_date)
        except ValueError:
            return messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format.")

        transaction_ids = [self.tree.item(item, "values")[0] for item in selected_items]

        if db_manager.mark_transactions_as_reconciled(transaction_ids, recon_date):
            messagebox.showinfo("Success", f"{len(transaction_ids)} transaction(s) marked as reconciled.")
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to reconcile transactions. Check logs.")
