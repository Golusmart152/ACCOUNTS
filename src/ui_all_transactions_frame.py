import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager
from .ui_invoice_detail_dialog import SalesInvoiceDetailDialog

class AllTransactionsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.all_tree_items = []
        self.transaction_map = {}
        self.create_filter_widgets()
        self.create_treeview()
        self.load_data()

    def create_filter_widgets(self):
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Transaction Type
        ctk.CTkLabel(filter_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.type_var = ctk.StringVar(value="All Transactions")
        self.type_menu = ctk.CTkOptionMenu(filter_frame, variable=self.type_var,
                                           values=["All Transactions", "Sales Invoices", "Purchase Invoices", "Payments Received", "Payments Made"])
        self.type_menu.grid(row=0, column=1, padx=5, pady=5)

        # Date Range
        ctk.CTkLabel(filter_frame, text="From:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)
        ctk.CTkLabel(filter_frame, text="To:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        # Party (Customer/Supplier)
        ctk.CTkLabel(filter_frame, text="Party:").grid(row=1, column=0, padx=5, pady=5)
        self.party_var = ctk.StringVar(value="All")
        self.party_menu = ctk.CTkComboBox(filter_frame, variable=self.party_var, values=["All"])
        self.party_menu.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Apply Button
        self.apply_button = ctk.CTkButton(filter_frame, text="Apply Filters", command=self.apply_filters)
        self.apply_button.grid(row=1, column=5, padx=10, pady=10, sticky="e")

    def create_treeview(self):
        tree_container = ctk.CTkFrame(self)
        tree_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("date", "type", "doc_number", "party", "amount")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.replace("_", " ").title())
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self.on_drill_down)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Search bar
        search_frame = ctk.CTkFrame(tree_container, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_var.trace_add("write", self.search_transactions)

    def search_transactions(self, *args):
        search_term = self.search_var.get().lower()

        # We need to re-insert all items to clear previous search, then detach the non-matching ones
        for iid in self.all_tree_items:
            self.tree.reattach(iid, '', 'end')

        if not search_term:
            return

        for iid in self.all_tree_items:
            item = self.tree.item(iid)
            values = [str(v).lower() for v in item['values']]
            if not any(search_term in v for v in values):
                self.tree.detach(iid)

    def load_data(self):
        # Load parties for the dropdown
        customers = [f"C: {c['name']}" for c in db_manager.get_all_customers()]
        suppliers = [f"S: {s['name']}" for s in db_manager.get_all_suppliers()]
        self.party_menu.configure(values=["All"] + customers + suppliers)
        self.party_menu.set("All")

        # Load initial transactions
        self.apply_filters()

    def apply_filters(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filters = {
            "transaction_type": self.type_var.get(),
            "start_date": self.start_date_entry.get() or None,
            "end_date": self.end_date_entry.get() or None,
        }

        party_selection = self.party_var.get()
        if party_selection != "All":
            party_type_char, party_name = party_selection.split(": ", 1)
            if party_type_char == "C":
                filters['party_type'] = "Customer"
                party = next((p for p in db_manager.get_all_customers() if p['name'] == party_name), None)
                if party: filters['party_id'] = party['id']
            elif party_type_char == "S":
                filters['party_type'] = "Supplier"
                party = next((p for p in db_manager.get_all_suppliers() if p['name'] == party_name), None)
                if party: filters['party_id'] = party['id']

        transactions = db_manager.get_all_transactions(filters)

        self.all_tree_items.clear()
        self.transaction_map.clear()
        for trans in transactions:
            iid = self.tree.insert("", "end", values=(trans['date'], trans['type'], trans['doc_number'], trans['party_name'], f"{trans['total_amount']:,.2f}"))
            self.all_tree_items.append(iid)
            self.transaction_map[iid] = trans

        # After populating, run the search to apply any existing search term
        self.search_transactions()

    def on_drill_down(self, event):
        item_id = self.tree.focus()
        if not item_id:
            return

        # The iid is the key in our transaction map
        transaction = self.transaction_map.get(item_id)
        if not transaction:
            return

        if transaction['type'] == 'Sales Invoice':
            invoice_header, invoice_items = db_manager.get_sales_invoice_details(transaction['id'])
            if invoice_header:
                SalesInvoiceDetailDialog(self, invoice_header, invoice_items)
            else:
                messagebox.showerror("Error", f"Could not find details for invoice ID {transaction['id']}", parent=self)
        else:
            messagebox.showinfo("Info", f"Drill-down for transaction type '{transaction['type']}' is not yet implemented.", parent=self)
