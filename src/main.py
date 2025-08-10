import customtkinter as ctk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import database_setup

# Import frames
from ui_dashboard_frame import DashboardFrame
from ui_godown_frame import GodownFrame
from ui_item_frame import ItemFrame
from ui_assembly_frame import AssemblyFrame
from ui_supplier_frame import SupplierFrame
from ui_purchase_frame import PurchaseFrame
from ui_customer_frame import CustomerFrame
from ui_sales_frame import SalesFrame
from ui_chart_of_accounts_frame import ChartOfAccountsFrame
from ui_customer_payment_frame import CustomerPaymentFrame
from ui_supplier_payment_frame import SupplierPaymentFrame
from ui_bank_reconciliation_frame import BankReconciliationFrame
from ui_warranty_report_frame import WarrantyReportFrame
from ui_amc_frame import AMCFrame
from ui_job_sheet_frame import JobSheetFrame
from ui_financial_reports_frame import FinancialReportsFrame
from ui_inventory_reports_frame import InventoryReportsFrame
from ui_search_frame import SearchFrame
from ui_settings_frame import SettingsFrame
from ui_unit_frame import UnitFrame
from ui_export_frame import ExportFrame
from ui_import_frame import ImportFrame
from ui_party_master_frame import PartyMasterFrame
from ui_all_transactions_frame import AllTransactionsFrame
from ui_hsn_frame import HSNFrame
import db_manager

# Xero-inspired color scheme
XERO_BLUE = "#13B5EA"
XERO_DARK_BLUE = "#0E7A9B"
XERO_LIGHT_BLUE = "#E8F7FC"
XERO_NAVY = "#1E3A8A"
XERO_GRAY = "#6B7280"
XERO_LIGHT_GRAY = "#F9FAFB"
XERO_WHITE = "#FFFFFF"
XERO_GREEN = "#10B981"
XERO_RED = "#EF4444"
XERO_ORANGE = "#F59E0B"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set Xero-inspired theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.title("FastFin - Modern Accounting Software")
        self.geometry("1400x900")
        self.configure(fg_color=XERO_LIGHT_GRAY)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create main layout
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        
        # Initialize frames
        self.initialize_frames()
        
        # Set default screen
        self.set_default_screen()

    def create_header(self):
        """Create Xero-style header with logo and user info"""
        self.header_frame = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=XERO_WHITE)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Logo and company name
        logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        ctk.CTkLabel(logo_frame, text="FastFin", 
                    font=ctk.CTkFont(size=28, weight="bold"), 
                    text_color=XERO_BLUE).pack(side="left")
        
        ctk.CTkLabel(logo_frame, text="Accounting", 
                    font=ctk.CTkFont(size=16), 
                    text_color=XERO_GRAY).pack(side="left", padx=(10, 0))
        
        # User info and actions
        user_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        user_frame.grid(row=0, column=1, padx=20, pady=15, sticky="e")
        
        ctk.CTkButton(user_frame, text="Settings", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=35,
                     command=self.settings_button_event).pack(side="right", padx=(10, 0))
        
        ctk.CTkLabel(user_frame, text="Welcome, Admin", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY).pack(side="right", padx=(0, 15))

    def create_sidebar(self):
        """Create Xero-style sidebar navigation"""
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=XERO_WHITE)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsw", padx=0, pady=0)
        self.sidebar_frame.grid_propagate(False)
        
        # Sidebar content with scrolling
        self.sidebar_scroll = ctk.CTkScrollableFrame(self.sidebar_frame, 
                                                    fg_color="transparent",
                                                    scrollbar_button_color=XERO_BLUE,
                                                    scrollbar_button_hover_color=XERO_DARK_BLUE)
        self.sidebar_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Dashboard button (always visible)
        self.create_nav_button("🏠 Dashboard", self.dashboard_button_event, is_primary=True)
        
        # Navigation sections
        self.create_nav_section("SALES & CUSTOMERS", [
            ("💰 Sales", self.sales_button_event),
            ("👥 Customers", self.customers_button_event),
            ("💳 Receive Payment", self.receive_payment_event)
        ])
        
        self.create_nav_section("PURCHASES & SUPPLIERS", [
            ("🛒 Purchases", self.purchases_button_event),
            ("🏢 Suppliers", self.suppliers_button_event),
            ("💸 Make Payment", self.make_payment_event)
        ])
        
        self.create_nav_section("INVENTORY", [
            ("📦 Items", self.items_button_event),
            ("🏪 Godowns", self.godowns_button_event),
            ("🔧 Assembly", self.assembly_button_event),
            ("📏 Units", self.units_button_event),
            ("🏷️ HSN/SAC Codes", self.hsn_button_event)
        ])
        
        self.create_nav_section("ACCOUNTING", [
            ("📊 All Transactions", self.all_transactions_button_event),
            ("📈 Chart of Accounts", self.coa_button_event),
            ("🏦 Bank Reconciliation", self.bank_recon_event)
        ])
        
        self.create_nav_section("SERVICES", [
            ("🔧 Job Sheets", self.job_sheet_event),
            ("📋 AMC Management", self.amc_event),
            ("⚠️ Warranty Report", self.warranty_report_event)
        ])
        
        self.create_nav_section("REPORTS", [
            ("💹 Financial Reports", self.financial_reports_event),
            ("📊 Inventory Reports", self.inventory_reports_event)
        ])
        
        self.create_nav_section("TOOLS", [
            ("🔍 Universal Search", self.search_button_event),
            ("📤 Export Data", self.export_button_event),
            ("📥 Import Data", self.import_button_event),
            ("👤 Party Master", self.party_master_button_event)
        ])

    def create_nav_section(self, title, buttons):
        """Create a navigation section with title and buttons"""
        # Section title
        title_frame = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent", height=40)
        title_frame.pack(fill="x", padx=15, pady=(20, 5))
        
        ctk.CTkLabel(title_frame, text=title, 
                    font=ctk.CTkFont(size=12, weight="bold"), 
                    text_color=XERO_GRAY,
                    anchor="w").pack(fill="x", pady=8)
        
        # Section buttons
        for text, command in buttons:
            self.create_nav_button(text, command)

    def create_nav_button(self, text, command, is_primary=False):
        """Create a Xero-style navigation button"""
        if is_primary:
            btn = ctk.CTkButton(self.sidebar_scroll, text=text,
                               font=ctk.CTkFont(size=16, weight="bold"),
                               fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                               corner_radius=8, height=45, anchor="w",
                               command=command)
        else:
            btn = ctk.CTkButton(self.sidebar_scroll, text=text,
                               font=ctk.CTkFont(size=14),
                               fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                               text_color=XERO_NAVY, corner_radius=8, height=40, anchor="w",
                               command=command)
        
        btn.pack(fill="x", padx=15, pady=2)
        return btn

    def create_main_content(self):
        """Create main content area"""
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.main_container.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def initialize_frames(self):
        """Initialize all application frames"""
        self.frames = {}
        
        frames_to_load = (
            DashboardFrame, GodownFrame, ItemFrame, HSNFrame, AssemblyFrame, 
            SupplierFrame, PurchaseFrame, CustomerFrame, SalesFrame, 
            ChartOfAccountsFrame, CustomerPaymentFrame, SupplierPaymentFrame, 
            BankReconciliationFrame, WarrantyReportFrame, AMCFrame, JobSheetFrame, 
            FinancialReportsFrame, SearchFrame, SettingsFrame, UnitFrame, 
            ExportFrame, ImportFrame, PartyMasterFrame, AllTransactionsFrame, 
            InventoryReportsFrame
        )
        
        for F in frames_to_load:
            frame = F(self.main_container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def set_default_screen(self):
        """Set the default startup screen"""
        default_screen_setting = db_manager.get_setting("default_startup_screen", "Dashboard")
        if default_screen_setting == "New Sale":
            self.sales_button_event()
        elif default_screen_setting == "New Purchase":
            self.purchases_button_event()
        elif default_screen_setting == "Universal Search":
            self.search_button_event()
        else:
            self.dashboard_button_event()

    # Navigation event handlers
    def show_frame(self, frame_name): 
        self.frames[frame_name].tkraise()
        
    def dashboard_button_event(self): 
        self.frames["DashboardFrame"].load_data(); self.show_frame("DashboardFrame")
        
    def search_button_event(self): 
        self.frames["SearchFrame"].load_data(); self.show_frame("SearchFrame")
        
    def hsn_button_event(self): 
        self.frames["HSNFrame"].load_data(); self.show_frame("HSNFrame")
        
    def godowns_button_event(self): 
        self.frames["GodownFrame"].load_godowns(); self.show_frame("GodownFrame")
        
    def items_button_event(self): 
        self.frames["ItemFrame"].load_data(); self.show_frame("ItemFrame")
        
    def assembly_button_event(self): 
        self.frames["AssemblyFrame"].load_data(); self.show_frame("AssemblyFrame")
        
    def suppliers_button_event(self): 
        self.frames["SupplierFrame"].load_data(); self.show_frame("SupplierFrame")
        
    def purchases_button_event(self): 
        self.frames["PurchaseFrame"].load_data(); self.show_frame("PurchaseFrame")
        
    def customers_button_event(self): 
        self.frames["CustomerFrame"].load_data(); self.show_frame("CustomerFrame")
        
    def sales_button_event(self): 
        self.frames["SalesFrame"].load_data(); self.show_frame("SalesFrame")
        
    def coa_button_event(self): 
        self.frames["ChartOfAccountsFrame"].load_data(); self.show_frame("ChartOfAccountsFrame")
        
    def receive_payment_event(self): 
        self.frames["CustomerPaymentFrame"].load_data(); self.show_frame("CustomerPaymentFrame")
        
    def make_payment_event(self): 
        self.frames["SupplierPaymentFrame"].load_data(); self.show_frame("SupplierPaymentFrame")
        
    def bank_recon_event(self): 
        self.frames["BankReconciliationFrame"].load_data(); self.show_frame("BankReconciliationFrame")
        
    def warranty_report_event(self): 
        self.frames["WarrantyReportFrame"].load_data(); self.show_frame("WarrantyReportFrame")
        
    def amc_event(self): 
        self.frames["AMCFrame"].load_data(); self.show_frame("AMCFrame")
        
    def job_sheet_event(self): 
        self.frames["JobSheetFrame"].load_data(); self.show_frame("JobSheetFrame")
        
    def financial_reports_event(self): 
        self.frames["FinancialReportsFrame"].load_data(); self.show_frame("FinancialReportsFrame")
        
    def inventory_reports_event(self): 
        self.frames["InventoryReportsFrame"].load_data(); self.show_frame("InventoryReportsFrame")
        
    def units_button_event(self): 
        self.frames["UnitFrame"].load_data(); self.show_frame("UnitFrame")
        
    def settings_button_event(self): 
        self.frames["SettingsFrame"].load_data(); self.show_frame("SettingsFrame")
        
    def export_button_event(self): 
        self.frames["ExportFrame"].load_data(); self.show_frame("ExportFrame")
        
    def import_button_event(self): 
        self.frames["ImportFrame"].load_data(); self.show_frame("ImportFrame")
        
    def party_master_button_event(self): 
        self.frames["PartyMasterFrame"].load_data(); self.show_frame("PartyMasterFrame")
        
    def all_transactions_button_event(self): 
        self.frames["AllTransactionsFrame"].load_data(); self.show_frame("AllTransactionsFrame")

if __name__ == "__main__":
    database_setup.setup_database()
    db_manager.initialize_chart_of_accounts()
    app = App()
    app.mainloop()
