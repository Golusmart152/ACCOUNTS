import customtkinter as ctk
from db import database_setup

# Import frames
from .ui_godown_frame import GodownFrame
from .ui_item_frame import ItemFrame
from .ui_assembly_frame import AssemblyFrame
from .ui_supplier_frame import SupplierFrame
from .ui_purchase_frame import PurchaseFrame
from .ui_customer_frame import CustomerFrame
from .ui_sales_frame import SalesFrame
from .ui_chart_of_accounts_frame import ChartOfAccountsFrame
from .ui_customer_payment_frame import CustomerPaymentFrame
from .ui_supplier_payment_frame import SupplierPaymentFrame
from .ui_bank_reconciliation_frame import BankReconciliationFrame
from .ui_warranty_report_frame import WarrantyReportFrame
from .ui_amc_frame import AMCFrame
from .ui_job_sheet_frame import JobSheetFrame
from .ui_financial_reports_frame import FinancialReportsFrame
from .ui_inventory_reports_frame import InventoryReportsFrame
from .ui_search_frame import SearchFrame
from .ui_settings_frame import SettingsFrame
from .ui_unit_frame import UnitFrame
from .ui_export_frame import ExportFrame
from .ui_import_frame import ImportFrame
from .ui_party_master_frame import PartyMasterFrame
from .ui_all_transactions_frame import AllTransactionsFrame
from .ui_hsn_frame import HSNFrame
from . import db_manager

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FastFin Accounting Software")
        self.geometry("1200x700")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkScrollableFrame(self, label_text="Menu", width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsw", rowspan=4)

        row_num = 0
        ctk.CTkLabel(self.sidebar_frame, text="FastFin", font=ctk.CTkFont(size=20, weight="bold")).grid(row=row_num, column=0, padx=20, pady=(20, 10)); row_num += 1
        ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.dashboard_button_event).grid(row=row_num, column=0, padx=20, pady=10, sticky="ew"); row_num += 1

        self.create_section("Search", [
            ("Universal Search", self.search_button_event)
        ], row_num); row_num += 2

        self.create_section("Import/Export", [
            ("Import Data", self.import_button_event),
            ("Export Data", self.export_button_event)
        ], row_num); row_num += 3

        self.create_section("Parties", [
            ("Party Master", self.party_master_button_event)
        ], row_num); row_num += 2

        # Sections
        self.create_section("Inventory", [
            ("Godowns", self.godowns_button_event),
            ("Items", self.items_button_event),
            ("HSN/SAC Codes", self.hsn_button_event),
            ("Assembly", self.assembly_button_event),
            ("Manage Units", self.units_button_event)
        ], row_num); row_num += 6

        self.create_section("Purchasing", [
            ("Suppliers", self.suppliers_button_event),
            ("New Purchase", self.purchases_button_event)
        ], row_num); row_num += 3

        self.create_section("Sales", [
            ("Customers", self.customers_button_event),
            ("New Sale", self.sales_button_event)
        ], row_num); row_num += 3

        self.create_section("Accounting", [
            ("All Transactions", self.all_transactions_button_event),
            ("Chart of Accounts", self.coa_button_event),
            ("Receive Payment", self.receive_payment_event),
            ("Make Payment", self.make_payment_event),
            ("Bank Reconciliation", self.bank_recon_event)
        ], row_num); row_num += 6

        self.create_section("Services & Reports", [
            ("Warranty Report", self.warranty_report_event),
            ("AMC Management", self.amc_event),
            ("Job Sheets", self.job_sheet_event),
            ("Financial Reports", self.financial_reports_event),
            ("Inventory Reports", self.inventory_reports_event)
        ], row_num); row_num += 6

        ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.settings_button_event).grid(row=row_num, column=0, padx=20, pady=10, sticky="ew"); row_num += 1

        # --- Main Content Area ---
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # --- Initialize All Frames ---
        frames_to_load = (GodownFrame, ItemFrame, HSNFrame, AssemblyFrame, SupplierFrame, PurchaseFrame, CustomerFrame, SalesFrame, ChartOfAccountsFrame, CustomerPaymentFrame, SupplierPaymentFrame, BankReconciliationFrame, WarrantyReportFrame, AMCFrame, JobSheetFrame, FinancialReportsFrame, SearchFrame, SettingsFrame, UnitFrame, ExportFrame, ImportFrame, PartyMasterFrame, AllTransactionsFrame)
        for F in frames_to_load:
            frame = F(self.main_container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.dashboard_frame = ctk.CTkFrame(self.main_container, corner_radius=0)
        ctk.CTkLabel(self.dashboard_frame, text="Welcome to the Dashboard!", font=ctk.CTkFont(size=18)).pack(pady=20)
        self.frames["Dashboard"] = self.dashboard_frame
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")

        default_screen_setting = db_manager.get_setting("default_startup_screen", "Dashboard")
        if default_screen_setting == "New Sale":
            self.sales_button_event()
        elif default_screen_setting == "New Purchase":
            self.purchases_button_event()
        elif default_screen_setting == "Universal Search":
            self.search_button_event()
        else:
            self.dashboard_button_event()

    def create_section(self, name, buttons, start_row):
        ctk.CTkLabel(self.sidebar_frame, text=name, font=ctk.CTkFont(weight="bold")).grid(row=start_row, column=0, padx=20, pady=(10,0), sticky="w")
        for i, (text, command) in enumerate(buttons):
            ctk.CTkButton(self.sidebar_frame, text=text, command=command, anchor="w").grid(row=start_row + i + 1, column=0, padx=20, pady=5, sticky="ew")

    def show_frame(self, frame_name): self.frames[frame_name].tkraise()
    def search_button_event(self): self.frames["SearchFrame"].load_data(); self.show_frame("SearchFrame")
    def dashboard_button_event(self): self.show_frame("Dashboard")
    def hsn_button_event(self): self.frames["HSNFrame"].load_data(); self.show_frame("HSNFrame")
    def godowns_button_event(self): self.frames["GodownFrame"].load_data(); self.show_frame("GodownFrame")
    def items_button_event(self): self.frames["ItemFrame"].load_data(); self.show_frame("ItemFrame")
    def assembly_button_event(self): self.frames["AssemblyFrame"].load_data(); self.show_frame("AssemblyFrame")
    def suppliers_button_event(self): self.frames["SupplierFrame"].load_data(); self.show_frame("SupplierFrame")
    def purchases_button_event(self): self.frames["PurchaseFrame"].load_data(); self.show_frame("PurchaseFrame")
    def customers_button_event(self): self.frames["CustomerFrame"].load_data(); self.show_frame("CustomerFrame")
    def sales_button_event(self): self.frames["SalesFrame"].load_data(); self.show_frame("SalesFrame")
    def coa_button_event(self): self.frames["ChartOfAccountsFrame"].load_data(); self.show_frame("ChartOfAccountsFrame")
    def receive_payment_event(self): self.frames["CustomerPaymentFrame"].load_data(); self.show_frame("CustomerPaymentFrame")
    def make_payment_event(self): self.frames["SupplierPaymentFrame"].load_data(); self.show_frame("SupplierPaymentFrame")
    def bank_recon_event(self): self.frames["BankReconciliationFrame"].load_data(); self.show_frame("BankReconciliationFrame")
    def warranty_report_event(self): self.frames["WarrantyReportFrame"].load_data(); self.show_frame("WarrantyReportFrame")
    def amc_event(self): self.frames["AMCFrame"].load_data(); self.show_frame("AMCFrame")
    def job_sheet_event(self): self.frames["JobSheetFrame"].load_data(); self.show_frame("JobSheetFrame")
    def financial_reports_event(self): self.frames["FinancialReportsFrame"].load_data(); self.show_frame("FinancialReportsFrame")
    def inventory_reports_event(self): self.frames["InventoryReportsFrame"].load_data(); self.show_frame("InventoryReportsFrame")
    def units_button_event(self): self.frames["UnitFrame"].load_data(); self.show_frame("UnitFrame")
    def settings_button_event(self): self.frames["SettingsFrame"].load_data(); self.show_frame("SettingsFrame")
    def export_button_event(self): self.frames["ExportFrame"].load_data(); self.show_frame("ExportFrame")
    def import_button_event(self): self.frames["ImportFrame"].load_data(); self.show_frame("ImportFrame")
    def party_master_button_event(self): self.frames["PartyMasterFrame"].load_data(); self.show_frame("PartyMasterFrame")
    def all_transactions_button_event(self): self.frames["AllTransactionsFrame"].load_data(); self.show_frame("AllTransactionsFrame")

if __name__ == "__main__":
    database_setup.setup_database()
    db_manager.initialize_chart_of_accounts()
    app = App()
    app.mainloop()
