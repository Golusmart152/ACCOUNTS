import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager
import datetime

class PartyMasterFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left frame for the list of parties
        self.list_frame = ctk.CTkFrame(self, width=250)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.list_frame, text="All Parties", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        columns = ("id", "name", "type")
        self.party_tree = ttk.Treeview(self.list_frame, columns=columns, show="headings")
        self.party_tree.heading("id", text="ID")
        self.party_tree.heading("name", text="Name")
        self.party_tree.heading("type", text="Type")
        self.party_tree.column("id", width=40)
        self.party_tree.column("type", width=80)
        self.party_tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.party_tree.bind("<<TreeviewSelect>>", self.on_party_select)

        # Right frame for the details
        self.detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.detail_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.detail_frame.grid_rowconfigure(0, weight=1)
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self.detail_frame)
        self.tab_view.pack(expand=True, fill="both")

        self.tab_view.add("Profile")
        self.tab_view.add("Transaction History")

        self.create_profile_tab(self.tab_view.tab("Profile"))
        self.create_history_tab(self.tab_view.tab("Transaction History"))

    def create_profile_tab(self, tab):
        tab.grid_columnconfigure(1, weight=1)
        self.profile_labels = {}

        # This will be populated dynamically when a party is selected
        ctk.CTkLabel(tab, text="Select a party from the list to view details.", font=ctk.CTkFont(size=14, slant="italic")).pack(pady=20)

    def create_history_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)

        history_frame = ctk.CTkFrame(tab, fg_color="transparent")
        history_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(0, weight=1)

        columns = ("date", "type", "doc_number", "debit", "credit", "balance")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        for col in columns: self.history_tree.heading(col, text=col.replace("_", " ").title())
        self.history_tree.grid(row=0, column=0, sticky="nsew")

        balance_frame = ctk.CTkFrame(tab)
        balance_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.balance_label = ctk.CTkLabel(balance_frame, text="Outstanding Balance: ₹0.00", font=ctk.CTkFont(weight="bold"))
        self.balance_label.pack(side="right", padx=10, pady=5)

        self.statement_button = ctk.CTkButton(balance_frame, text="Generate Statement", command=self.open_statement_dialog)
        self.statement_button.pack(side="left", padx=10, pady=5)

    def load_data(self):
        """Load all customers and suppliers into the master list."""
        for item in self.party_tree.get_children():
            self.party_tree.delete(item)

        customers = db_manager.get_all_customers()
        for cust in customers:
            self.party_tree.insert("", "end", values=(cust['id'], cust['name'], "Customer"), tags=("Customer",))

        suppliers = db_manager.get_all_suppliers()
        for supp in suppliers:
            self.party_tree.insert("", "end", values=(supp['id'], supp['name'], "Supplier"), tags=("Supplier",))

    def on_party_select(self, event):
        selected_item = self.party_tree.focus()
        if not selected_item:
            return

        item_values = self.party_tree.item(selected_item, "values")
        party_id = item_values[0]
        party_type = item_values[2]

        # For now, just display a placeholder. Detailed view will be built out.
        self.display_party_profile(party_id, party_type)
        self.display_party_history(party_id, party_type)

    def display_party_profile(self, party_id, party_type):
        # Clear previous profile
        for widget in self.tab_view.tab("Profile").winfo_children():
            widget.destroy()

        # Fetch full details
        if party_type == "Customer":
            # In a real scenario, we'd have a get_customer_by_id function.
            # For now, we'll filter the full list.
            party = next((c for c in db_manager.get_all_customers() if c['id'] == int(party_id)), None)
        else: # Supplier
            party = next((s for s in db_manager.get_all_suppliers() if s['id'] == int(party_id)), None)

        if not party:
            ctk.CTkLabel(self.tab_view.tab("Profile"), text="Could not load party details.").pack(pady=20)
            return

        row = 0
        for key, value in party.items():
            ctk.CTkLabel(self.tab_view.tab("Profile"), text=f"{key.replace('_', ' ').title()}:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
            ctk.CTkLabel(self.tab_view.tab("Profile"), text=value).grid(row=row, column=1, padx=10, pady=5, sticky="w")
            row += 1

    def display_party_history(self, party_id, party_type):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        if party_type == "Customer":
            transactions = db_manager.get_transactions_for_customer(party_id)
        else: # Supplier
            transactions = db_manager.get_transactions_for_supplier(party_id)

        balance = 0.0
        for trans in transactions:
            debit = trans['debit'] or 0.0
            credit = trans['credit'] or 0.0
            # For customers, debit is what they owe us, credit is what they paid. Balance = Dr - Cr
            # For suppliers, debit is what they owe us (e.g. returns), credit is what we owe them. Balance = Cr - Dr
            if party_type == "Customer":
                balance += (debit - credit)
            else: # Supplier
                balance += (credit - debit)

            self.history_tree.insert("", "end", values=(
                trans['date'], trans['type'], trans['document_number'],
                f"{debit:,.2f}", f"{credit:,.2f}", f"{balance:,.2f}"
            ))

        balance_text = "Receivable" if party_type == "Customer" else "Payable"
        self.balance_label.configure(text=f"Closing Balance: ₹{balance:,.2f} {balance_text}")

    def open_statement_dialog(self):
        selected_item = self.party_tree.focus()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a party from the list first.", parent=self)
            return

        dialog = DateRangeDialog(self)
        dates = dialog.get_dates()

        if dates:
            start_date, end_date = dates
            item_values = self.party_tree.item(selected_item, "values")
            party_id = int(item_values[0])
            party_type = item_values[2]

            self.generate_statement(party_id, party_type, start_date, end_date)

    def generate_statement(self, party_id, party_type, start_date, end_date):
        import pdf_generator # Import here to avoid circular dependency issues at startup

        party_details = db_manager.get_all_customers() if party_type == "Customer" else db_manager.get_all_suppliers()
        party = next((p for p in party_details if p['id'] == party_id), None)

        if not party: return messagebox.showerror("Error", "Could not find party details.", parent=self)

        opening_balance, transactions = db_manager.get_account_statement_data(party_id, party_type, start_date, end_date)

        filename = filedialog.asksaveasfilename(
            title=f"Save Statement for {party['name']}",
            initialfile=f"Statement_{party['name']}_{start_date}_to_{end_date}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")]
        )
        if not filename: return

        success, error = pdf_generator.generate_account_statement_pdf(filename, party, start_date, end_date, opening_balance, transactions)

        if success:
            messagebox.showinfo("Success", f"Statement saved successfully to:\n{filename}", parent=self)
        else:
            messagebox.showerror("Error", f"Failed to generate PDF: {error}", parent=self)


class DateRangeDialog(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Select Date Range")
        self.geometry("300x180")
        self.transient(master)
        self.grab_set()

        self.start_date_var = ctk.StringVar(value=datetime.date.today().replace(day=1).isoformat())
        self.end_date_var = ctk.StringVar(value=datetime.date.today().isoformat())
        self.dates = None

        ctk.CTkLabel(self, text="Start Date (YYYY-MM-DD):").pack(pady=(10,0))
        ctk.CTkEntry(self, textvariable=self.start_date_var).pack(pady=5)
        ctk.CTkLabel(self, text="End Date (YYYY-MM-DD):").pack(pady=5)
        ctk.CTkEntry(self, textvariable=self.end_date_var).pack(pady=5)

        ok_button = ctk.CTkButton(self, text="OK", command=self.on_ok)
        ok_button.pack(pady=10)

        self.wait_window()

    def on_ok(self):
        # Basic validation can be added here
        self.dates = (self.start_date_var.get(), self.end_date_var.get())
        self.destroy()

    def get_dates(self):
        return self.dates
