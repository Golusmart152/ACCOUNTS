import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
from . import db_manager
import datetime

class AMCFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.selected_amc_id = None
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Manage Annual Maintenance Contracts (AMCs)", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Top frame for adding new AMCs ---
        add_amc_frame = ctk.CTkFrame(self)
        add_amc_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.create_add_amc_form(add_amc_frame)

        # --- Bottom frame for lists ---
        lists_frame = ctk.CTkFrame(self)
        lists_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
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

    def load_data(self):
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])
        self.load_amcs()
        self.clear_service_calls()
        self.add_service_call_button.configure(state="disabled")

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
