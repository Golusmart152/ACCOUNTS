import customtkinter as ctk
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

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Create Xero-style dashboard layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Dashboard header
        self.create_header()
        
        # Main dashboard content
        self.create_dashboard_content()

    def create_header(self):
        """Create dashboard header with title and actions"""
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=XERO_WHITE)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        # Title section
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        ctk.CTkLabel(title_frame, text="Dashboard", 
                    font=ctk.CTkFont(size=32, weight="bold"), 
                    text_color=XERO_NAVY).pack(anchor="w")
        
        ctk.CTkLabel(title_frame, text="Get insights into your business performance", 
                    font=ctk.CTkFont(size=16), 
                    text_color=XERO_GRAY).pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, padx=30, pady=20, sticky="e")
        
        ctk.CTkButton(actions_frame, text="+ New Sale", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=40, width=120,
                     command=self.navigate_to_sales).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(actions_frame, text="+ New Purchase", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                     text_color=XERO_BLUE, border_color=XERO_BLUE, border_width=2,
                     corner_radius=8, height=40, width=140,
                     command=self.navigate_to_purchases).pack(side="right")

    def create_dashboard_content(self):
        """Create main dashboard content with metrics and widgets"""
        # Scrollable content area
        content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                               scrollbar_button_color=XERO_BLUE,
                                               scrollbar_button_hover_color=XERO_DARK_BLUE)
        content_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        content_scroll.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Key metrics cards row
        self.create_metrics_cards(content_scroll)
        
        # Charts and insights row
        self.create_insights_section(content_scroll)
        
        # Quick actions and recent activity row
        self.create_activity_section(content_scroll)

    def create_metrics_cards(self, parent):
        """Create Xero-style key performance indicator cards"""
        # Metrics section title
        metrics_title_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        metrics_title_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(metrics_title_frame, text="Key Metrics", 
                    font=ctk.CTkFont(size=24, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=15)
        
        # Revenue card
        self.revenue_card = self.create_metric_card(parent, 0, 1, "Revenue", "₹0", "+0%", XERO_GREEN)
        
        # Expenses card
        self.expenses_card = self.create_metric_card(parent, 1, 1, "Expenses", "₹0", "+0%", XERO_RED)
        
        # Profit card
        self.profit_card = self.create_metric_card(parent, 2, 1, "Net Profit", "₹0", "+0%", XERO_BLUE)
        
        # Outstanding card
        self.outstanding_card = self.create_metric_card(parent, 3, 1, "Outstanding", "₹0", "0 invoices", XERO_ORANGE)

    def create_metric_card(self, parent, col, row, title, value, subtitle, color):
        """Create a single Xero-style metric card"""
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=XERO_WHITE, 
                           border_width=1, border_color="#E5E7EB")
        card.grid(row=row, column=col, padx=15, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        
        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Title
        ctk.CTkLabel(content_frame, text=title, 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_GRAY, anchor="w").pack(fill="x")
        
        # Value
        value_label = ctk.CTkLabel(content_frame, text=value, 
                                  font=ctk.CTkFont(size=36, weight="bold"), 
                                  text_color=XERO_NAVY, anchor="w")
        value_label.pack(fill="x", pady=(10, 5))
        
        # Subtitle/Change indicator
        ctk.CTkLabel(content_frame, text=subtitle, 
                    font=ctk.CTkFont(size=14), 
                    text_color=color, anchor="w").pack(fill="x")
        
        # Store reference to value label for updates
        return {"card": card, "value_label": value_label}

    def create_insights_section(self, parent):
        """Create business insights section without charts"""
        # Section title
        insights_title_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        insights_title_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(insights_title_frame, text="Business Overview",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=15)
        
        # Top customers card
        customers_card = ctk.CTkFrame(parent, corner_radius=12, fg_color=XERO_WHITE,
                                     border_width=1, border_color="#E5E7EB")
        customers_card.grid(row=3, column=0, columnspan=2, padx=15, pady=10, sticky="ew")
        
        customers_content = ctk.CTkFrame(customers_card, fg_color="transparent")
        customers_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(customers_content, text="Top Customers",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=XERO_NAVY, anchor="w").pack(fill="x")
        
        # Customer list
        self.customers_list = ctk.CTkFrame(customers_content, fg_color="transparent")
        self.customers_list.pack(fill="x", pady=(15, 0))
        
        # Top suppliers card
        suppliers_card = ctk.CTkFrame(parent, corner_radius=12, fg_color=XERO_WHITE,
                                     border_width=1, border_color="#E5E7EB")
        suppliers_card.grid(row=3, column=2, columnspan=2, padx=15, pady=10, sticky="ew")
        
        suppliers_content = ctk.CTkFrame(suppliers_card, fg_color="transparent")
        suppliers_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(suppliers_content, text="Top Suppliers",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=XERO_NAVY, anchor="w").pack(fill="x")
        
        # Supplier list
        self.suppliers_list = ctk.CTkFrame(suppliers_content, fg_color="transparent")
        self.suppliers_list.pack(fill="x", pady=(15, 0))

    def create_activity_section(self, parent):
        """Create quick actions and recent activity section"""
        # Section title
        activity_title_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        activity_title_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=30, pady=(30, 10))
        
        ctk.CTkLabel(activity_title_frame, text="Quick Actions & Recent Activity", 
                    font=ctk.CTkFont(size=24, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=15)
        
        # Quick actions card
        actions_card = ctk.CTkFrame(parent, corner_radius=12, fg_color=XERO_WHITE,
                                   border_width=1, border_color="#E5E7EB")
        actions_card.grid(row=5, column=0, columnspan=2, padx=15, pady=10, sticky="ew")
        
        actions_content = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(actions_content, text="Quick Actions", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x")
        
        # Action buttons grid
        actions_grid = ctk.CTkFrame(actions_content, fg_color="transparent")
        actions_grid.pack(fill="x", pady=(15, 0))
        actions_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Quick action buttons
        quick_actions = [
            ("💰 Create Invoice", self.navigate_to_sales),
            ("🛒 Record Purchase", self.navigate_to_purchases),
            ("👥 Add Customer", self.navigate_to_customers),
            ("🏢 Add Supplier", self.navigate_to_suppliers),
            ("📦 Add Item", self.navigate_to_items),
            ("🔍 Search Records", self.navigate_to_search)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(actions_grid, text=text,
                               font=ctk.CTkFont(size=14, weight="bold"),
                               fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                               text_color=XERO_BLUE, corner_radius=8, height=45,
                               anchor="w", command=command)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        # Recent activity card
        activity_card = ctk.CTkFrame(parent, corner_radius=12, fg_color=XERO_WHITE,
                                    border_width=1, border_color="#E5E7EB")
        activity_card.grid(row=5, column=2, columnspan=2, padx=15, pady=10, sticky="ew")
        
        activity_content = ctk.CTkFrame(activity_card, fg_color="transparent")
        activity_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        ctk.CTkLabel(activity_content, text="Recent Activity", 
                    font=ctk.CTkFont(size=18, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x")
        
        # Recent activity list
        self.activity_list = ctk.CTkScrollableFrame(activity_content, height=200,
                                                   fg_color="transparent",
                                                   scrollbar_button_color=XERO_BLUE)
        self.activity_list.pack(fill="both", expand=True, pady=(15, 0))

    def load_data(self):
        """Load and display dashboard data"""
        try:
            # Load financial metrics
            self.load_financial_metrics()
            
            # Load top customers
            self.load_top_customers()
            
            # Load top suppliers
            self.load_top_suppliers()
            
            # Load recent activity
            self.load_recent_activity()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.load_default_data()

    def load_financial_metrics(self):
        """Load financial metrics from database"""
        try:
            # Get current month data
            sales_data = db_manager.get_monthly_sales_summary()
            purchase_data = db_manager.get_monthly_purchase_summary()
            receivables_data = db_manager.get_overdue_receivables_summary()
            
            # Update revenue card
            revenue = sales_data.get('total', 0) if sales_data else 0
            self.revenue_card["value_label"].configure(text=f"₹{revenue:,.0f}")
            
            # Update expenses card
            expenses = purchase_data.get('total', 0) if purchase_data else 0
            self.expenses_card["value_label"].configure(text=f"₹{expenses:,.0f}")
            
            # Update profit card
            profit = revenue - expenses
            self.profit_card["value_label"].configure(text=f"₹{profit:,.0f}")
            
            # Update outstanding card
            outstanding = receivables_data.get('total', 0) if receivables_data else 0
            outstanding_count = receivables_data.get('count', 0) if receivables_data else 0
            self.outstanding_card["value_label"].configure(text=f"₹{outstanding:,.0f}")
            
        except Exception as e:
            print(f"Error loading financial metrics: {e}")
            self.load_default_data()

    def load_top_customers(self):
        """Load top customers list"""
        try:
            # Clear existing customers
            for widget in self.customers_list.winfo_children():
                widget.destroy()
            
            # Get top customers (placeholder - implement in db_manager)
            customers = [
                {"name": "ABC Corporation", "amount": 125000},
                {"name": "XYZ Industries", "amount": 98000},
                {"name": "Tech Solutions Ltd", "amount": 75000},
                {"name": "Global Enterprises", "amount": 62000}
            ]
            
            for customer in customers:
                customer_frame = ctk.CTkFrame(self.customers_list, fg_color="transparent")
                customer_frame.pack(fill="x", pady=2)
                customer_frame.grid_columnconfigure(1, weight=1)
                
                ctk.CTkLabel(customer_frame, text=customer["name"],
                            font=ctk.CTkFont(size=14),
                            text_color=XERO_NAVY, anchor="w").grid(row=0, column=0, sticky="w")
                
                ctk.CTkLabel(customer_frame, text=f"₹{customer['amount']:,.0f}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=XERO_GREEN, anchor="e").grid(row=0, column=1, sticky="e")
                
        except Exception as e:
            print(f"Error loading top customers: {e}")

    def load_top_suppliers(self):
        """Load top suppliers list"""
        try:
            # Clear existing suppliers
            for widget in self.suppliers_list.winfo_children():
                widget.destroy()
            
            # Get top suppliers (placeholder - implement in db_manager)
            suppliers = [
                {"name": "Tech Components Ltd", "amount": 89000},
                {"name": "Office Supplies Co", "amount": 67000},
                {"name": "Hardware Solutions", "amount": 54000},
                {"name": "Digital Systems Inc", "amount": 43000}
            ]
            
            for supplier in suppliers:
                supplier_frame = ctk.CTkFrame(self.suppliers_list, fg_color="transparent")
                supplier_frame.pack(fill="x", pady=2)
                supplier_frame.grid_columnconfigure(1, weight=1)
                
                ctk.CTkLabel(supplier_frame, text=supplier["name"],
                            font=ctk.CTkFont(size=14),
                            text_color=XERO_NAVY, anchor="w").grid(row=0, column=0, sticky="w")
                
                ctk.CTkLabel(supplier_frame, text=f"₹{supplier['amount']:,.0f}",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            text_color=XERO_RED, anchor="e").grid(row=0, column=1, sticky="e")
                
        except Exception as e:
            print(f"Error loading top suppliers: {e}")

    def load_recent_activity(self):
        """Load recent activity feed"""
        try:
            # Clear existing activity
            for widget in self.activity_list.winfo_children():
                widget.destroy()
            
            # Get recent activities
            activities = db_manager.get_recent_activities(limit=10) if hasattr(db_manager, 'get_recent_activities') else []
            
            if not activities:
                # Sample activities
                activities = [
                    {"type": "sale", "description": "Created invoice INV-2024-001 for ABC Corp", "time": "2 hours ago"},
                    {"type": "purchase", "description": "Recorded purchase PO-2024-015 from XYZ Suppliers", "time": "4 hours ago"},
                    {"type": "payment", "description": "Received payment ₹25,000 from Tech Solutions", "time": "1 day ago"},
                    {"type": "customer", "description": "Added new customer: Global Enterprises Ltd", "time": "2 days ago"},
                    {"type": "item", "description": "Updated inventory for Laptop Model X", "time": "3 days ago"}
                ]
            
            for activity in activities:
                activity_frame = ctk.CTkFrame(self.activity_list, fg_color="transparent")
                activity_frame.pack(fill="x", pady=5)
                
                # Activity icon based on type
                icon_map = {
                    "sale": "💰", "purchase": "🛒", "payment": "💳", 
                    "customer": "👥", "item": "📦", "default": "📋"
                }
                icon = icon_map.get(activity.get("type", ""), icon_map["default"])
                
                ctk.CTkLabel(activity_frame, text=f"{icon} {activity.get('description', 'Unknown activity')}", 
                            font=ctk.CTkFont(size=13), 
                            text_color=XERO_NAVY, anchor="w").pack(fill="x")
                
                if activity.get("time"):
                    ctk.CTkLabel(activity_frame, text=activity["time"], 
                                font=ctk.CTkFont(size=11), 
                                text_color=XERO_GRAY, anchor="w").pack(fill="x")
                
        except Exception as e:
            print(f"Error loading recent activity: {e}")

    def load_default_data(self):
        """Load default data when database calls fail"""
        self.revenue_card["value_label"].configure(text="₹0")
        self.expenses_card["value_label"].configure(text="₹0")
        self.profit_card["value_label"].configure(text="₹0")
        self.outstanding_card["value_label"].configure(text="₹0")

    # Navigation methods
    def navigate_to_sales(self):
        if hasattr(self.master, 'sales_button_event'):
            self.master.sales_button_event()

    def navigate_to_purchases(self):
        if hasattr(self.master, 'purchases_button_event'):
            self.master.purchases_button_event()

    def navigate_to_customers(self):
        if hasattr(self.master, 'customers_button_event'):
            self.master.customers_button_event()

    def navigate_to_suppliers(self):
        if hasattr(self.master, 'suppliers_button_event'):
            self.master.suppliers_button_event()

    def navigate_to_items(self):
        if hasattr(self.master, 'items_button_event'):
            self.master.items_button_event()

    def navigate_to_search(self):
        if hasattr(self.master, 'search_button_event'):
            self.master.search_button_event()