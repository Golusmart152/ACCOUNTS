import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

# Xero Color Scheme
XERO_BLUE = "#13B5EA"
XERO_NAVY = "#1E3A8A"
XERO_WHITE = "#FFFFFF"
XERO_LIGHT_GRAY = "#F9FAFB"
XERO_GRAY = "#6B7280"
XERO_DARK_GRAY = "#374151"
XERO_GREEN = "#10B981"
XERO_RED = "#EF4444"

class SupplierFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.create_widgets()
        self.load_suppliers()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container with Xero styling
        main_container = ctk.CTkFrame(self, fg_color=XERO_WHITE, corner_radius=12)
        main_container.grid(row=0, column=0, padx=25, pady=25, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # Xero-style header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=25, pady=25, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Main title with Xero typography
        ctk.CTkLabel(header_frame, text="Suppliers",
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, sticky="w")
        
        # Action button with Xero styling
        add_button = ctk.CTkButton(header_frame, text="+ Add Supplier",
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                  corner_radius=8, height=40,
                                  command=self.open_supplier_dialog)
        add_button.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        # Search bar with Xero styling
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(20, 0))
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(search_frame,
                                        placeholder_text="Search suppliers by name, GSTIN, or location...",
                                        font=ctk.CTkFont(size=14),
                                        height=40, corner_radius=8,
                                        border_color=XERO_GRAY)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", self.filter_suppliers)
        
        # View toggle with Xero styling
        view_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        view_frame.grid(row=0, column=1, sticky="e")
        
        self.card_view_button = ctk.CTkButton(view_frame, text="Card View",
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                             corner_radius=6, height=32, width=80,
                                             command=self.show_card_view)
        self.card_view_button.pack(side="left", padx=2)
        
        self.table_view_button = ctk.CTkButton(view_frame, text="Table View",
                                              font=ctk.CTkFont(size=12, weight="bold"),
                                              fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                              text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                              corner_radius=6, height=32, width=80,
                                              command=self.show_table_view)
        self.table_view_button.pack(side="left", padx=2)
        
        # Content area with Xero styling
        content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        content_container.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(0, weight=1)
        
        # Create both views
        self.create_card_view(content_container)
        self.create_table_view(content_container)
        
        # Initialize supplier cards
        self.supplier_cards = []
        
        # Show card view by default
        self.show_card_view()
        
    def create_card_view(self, parent):
        """Create Xero-style card view for suppliers"""
        self.card_view_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.card_view_frame.grid(row=0, column=0, sticky="nsew")
        self.card_view_frame.grid_columnconfigure(0, weight=1)
        self.card_view_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable content area
        self.card_content_frame = ctk.CTkScrollableFrame(self.card_view_frame,
                                                        fg_color="transparent",
                                                        corner_radius=0)
        self.card_content_frame.grid(row=0, column=0, sticky="nsew")
        self.card_content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
    def create_table_view(self, parent):
        """Create Xero-style table view for suppliers"""
        self.table_view_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.table_view_frame.grid(row=0, column=0, sticky="nsew")
        self.table_view_frame.grid_columnconfigure(0, weight=1)
        self.table_view_frame.grid_rowconfigure(1, weight=1)
        
        # Form section with Xero styling
        form_container = ctk.CTkFrame(self.table_view_frame, fg_color=XERO_WHITE, corner_radius=12)
        form_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        form_container.grid_columnconfigure((1, 3), weight=1)
        
        # Form title
        ctk.CTkLabel(form_container, text="Supplier Information",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, columnspan=4,
                                              padx=25, pady=(25, 20), sticky="w")
        
        # Form fields with Xero styling
        ctk.CTkLabel(form_container, text="Supplier Name",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=0, padx=(25, 10), pady=8, sticky="w")
        self.name_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                      height=40, corner_radius=8, border_color=XERO_GRAY)
        self.name_entry.grid(row=1, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Phone Number",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        self.phone_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY)
        self.phone_entry.grid(row=1, column=3, padx=(0, 25), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="GSTIN",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, padx=(25, 10), pady=8, sticky="w")
        self.gstin_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY)
        self.gstin_entry.grid(row=2, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Email Address",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=2, padx=(0, 10), pady=8, sticky="w")
        self.email_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY)
        self.email_entry.grid(row=2, column=3, padx=(0, 25), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="Address",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=3, column=0, padx=(25, 10), pady=8, sticky="w")
        self.address_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                         height=40, corner_radius=8, border_color=XERO_GRAY)
        self.address_entry.grid(row=3, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(form_container, text="State",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=3, column=2, padx=(0, 10), pady=8, sticky="w")
        self.state_entry = ctk.CTkEntry(form_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY,
                                       placeholder_text="e.g., Maharashtra")
        self.state_entry.grid(row=3, column=3, padx=(0, 25), pady=8, sticky="ew")
        
        # Action buttons with Xero styling
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=4, padx=25, pady=(20, 25), sticky="e")
        
        self.clear_button = ctk.CTkButton(button_frame, text="Clear",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                         text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                         corner_radius=8, height=40, width=100,
                                         command=self.clear_form)
        self.clear_button.pack(side="right", padx=5)
        
        self.update_button = ctk.CTkButton(button_frame, text="Update Supplier",
                                          font=ctk.CTkFont(size=14, weight="bold"),
                                          fg_color=XERO_GREEN, hover_color="#059669",
                                          corner_radius=8, height=40, width=140,
                                          command=self.update_supplier, state="disabled")
        self.update_button.pack(side="right", padx=5)
        
        self.add_button = ctk.CTkButton(button_frame, text="Add Supplier",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                       corner_radius=8, height=40, width=140,
                                       command=self.add_supplier)
        self.add_button.pack(side="right", padx=5)
        
        # Table container with Xero styling
        table_container = ctk.CTkFrame(self.table_view_frame, fg_color=XERO_WHITE, corner_radius=12)
        table_container.grid(row=1, column=0, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)
        
        # Table title
        ctk.CTkLabel(table_container, text="All Suppliers",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, padx=25, pady=(25, 15), sticky="w")
        
        # Treeview with modern styling
        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        tree_frame.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("id", "name", "gstin", "phone", "email", "address", "state")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Configure column headings with better formatting
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Supplier Name")
        self.tree.heading("gstin", text="GSTIN")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("email", text="Email")
        self.tree.heading("address", text="Address")
        self.tree.heading("state", text="State")
        
        # Configure column widths
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("gstin", width=150)
        self.tree.column("phone", width=120)
        self.tree.column("email", width=180)
        self.tree.column("address", width=250)
        self.tree.column("state", width=120)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
    def show_card_view(self):
        """Show card view and hide table view"""
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid_remove()
        if hasattr(self, 'card_view_frame'):
            self.card_view_frame.grid()
        
        # Update button states
        self.card_view_button.configure(fg_color=XERO_BLUE, text_color=XERO_WHITE)
        self.table_view_button.configure(fg_color="transparent", text_color=XERO_GRAY)
        
        self.current_view = "card"
        self.load_suppliers_cards()
        
    def show_table_view(self):
        """Show table view and hide card view"""
        if hasattr(self, 'card_view_frame'):
            self.card_view_frame.grid_remove()
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid()
        
        # Update button states
        self.table_view_button.configure(fg_color=XERO_BLUE, text_color=XERO_WHITE)
        self.card_view_button.configure(fg_color="transparent", text_color=XERO_GRAY)
        
        self.current_view = "table"
        self.load_suppliers_table()
        
    def filter_suppliers(self, event=None):
        """Filter suppliers based on search text"""
        search_term = self.search_entry.get().lower()
        if hasattr(self, 'current_view') and self.current_view == "card":
            self.load_suppliers_cards(search_term)
        else:
            self.load_suppliers_table(search_term)
        
    def open_supplier_dialog(self):
        """Open Xero-style dialog to add or edit a supplier"""
        # Create a top-level window with Xero styling
        self.supplier_dialog = ctk.CTkToplevel(self)
        self.supplier_dialog.title("Supplier Details")
        self.supplier_dialog.geometry("500x600")
        self.supplier_dialog.resizable(False, False)
        self.supplier_dialog.transient(self)
        self.supplier_dialog.grab_set()
        self.supplier_dialog.configure(fg_color=XERO_LIGHT_GRAY)
        
        # Main form container with Xero styling
        form_container = ctk.CTkFrame(self.supplier_dialog, fg_color=XERO_WHITE, corner_radius=12)
        form_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Dialog title
        ctk.CTkLabel(form_container, text="Supplier Information",
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=XERO_NAVY).pack(padx=25, pady=(25, 20), anchor="w")
        
        # Form fields with Xero styling
        fields_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        fields_frame.grid_columnconfigure(0, weight=1)
        
        # Supplier Name
        ctk.CTkLabel(fields_frame, text="Supplier Name",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.dialog_name_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                             height=40, corner_radius=8, border_color=XERO_GRAY)
        self.dialog_name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # GSTIN
        ctk.CTkLabel(fields_frame, text="GSTIN",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.dialog_gstin_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                              height=40, corner_radius=8, border_color=XERO_GRAY)
        self.dialog_gstin_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        # Phone
        ctk.CTkLabel(fields_frame, text="Phone Number",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.dialog_phone_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                              height=40, corner_radius=8, border_color=XERO_GRAY)
        self.dialog_phone_entry.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(fields_frame, text="Email Address",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.dialog_email_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                              height=40, corner_radius=8, border_color=XERO_GRAY)
        self.dialog_email_entry.grid(row=7, column=0, sticky="ew", pady=(0, 15))
        
        # Address
        ctk.CTkLabel(fields_frame, text="Address",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=8, column=0, sticky="w", pady=(0, 5))
        self.dialog_address_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                                height=40, corner_radius=8, border_color=XERO_GRAY)
        self.dialog_address_entry.grid(row=9, column=0, sticky="ew", pady=(0, 15))
        
        # State
        ctk.CTkLabel(fields_frame, text="State",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=10, column=0, sticky="w", pady=(0, 5))
        self.dialog_state_entry = ctk.CTkEntry(fields_frame, font=ctk.CTkFont(size=14),
                                              height=40, corner_radius=8, border_color=XERO_GRAY,
                                              placeholder_text="e.g., Maharashtra")
        self.dialog_state_entry.grid(row=11, column=0, sticky="ew", pady=(0, 15))
        
        # Action buttons with Xero styling
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        cancel_button = ctk.CTkButton(button_frame, text="Cancel",
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                     text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                     corner_radius=8, height=40, width=120,
                                     command=self.supplier_dialog.destroy)
        cancel_button.pack(side="right", padx=5)
        
        self.dialog_save_button = ctk.CTkButton(button_frame, text="Save Supplier",
                                               font=ctk.CTkFont(size=14, weight="bold"),
                                               fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                               corner_radius=8, height=40, width=140,
                                               command=self.save_supplier_from_dialog)
        self.dialog_save_button.pack(side="right", padx=5)
        
        # Focus on name entry
        self.dialog_name_entry.focus()
        
    def save_supplier_from_dialog(self):
        """Save supplier from dialog form"""
        name = self.dialog_name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Supplier Name is required.")
            return
            
        data = (
            name,
            self.dialog_gstin_entry.get().strip(),
            self.dialog_address_entry.get().strip(),
            self.dialog_phone_entry.get().strip(),
            self.dialog_email_entry.get().strip(),
            self.dialog_state_entry.get().strip()
        )
        
        if db_manager.add_supplier(*data):
            messagebox.showinfo("Success", "Supplier added successfully.")
            self.supplier_dialog.destroy()
            self.load_suppliers()
        else:
            messagebox.showerror("Database Error", f"Could not add supplier. '{data[0]}' may already exist.")

    def load_suppliers_cards(self, search_term=""):
        """Load suppliers as Xero-style cards"""
        # Clear existing cards
        for card in self.supplier_cards:
            card.destroy()
        self.supplier_cards = []
        
        # Get suppliers from database
        suppliers = db_manager.get_all_suppliers()
        
        # Filter suppliers if search term provided
        if search_term:
            suppliers = [supplier for supplier in suppliers if 
                        search_term in supplier['name'].lower() or 
                        search_term in (supplier['gstin'] or '').lower() or
                        search_term in (supplier['state'] or '').lower()]
        
        # Create cards for each supplier
        for i, supplier in enumerate(suppliers):
            card = self.create_supplier_card(supplier)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
            self.supplier_cards.append(card)
            
    def create_supplier_card(self, supplier):
        """Create a Xero-style card for a supplier"""
        card_frame = ctk.CTkFrame(self.card_content_frame, fg_color=XERO_WHITE, corner_radius=12)
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Supplier name header with Xero styling
        header_frame = ctk.CTkFrame(card_frame, fg_color=XERO_BLUE, corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        header_frame.grid_columnconfigure(0, weight=1)
        
        name_label = ctk.CTkLabel(header_frame, text=supplier['name'], 
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 text_color=XERO_WHITE)
        name_label.pack(pady=15)
        
        # Supplier details with Xero styling
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        details_frame.grid_columnconfigure(1, weight=1)
        
        # GSTIN
        ctk.CTkLabel(details_frame, text="GSTIN:", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=0, column=0, sticky="w", pady=3)
        ctk.CTkLabel(details_frame, text=supplier['gstin'] or "N/A", 
                    font=ctk.CTkFont(size=12),
                    text_color=XERO_GRAY).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)
        
        # Phone
        ctk.CTkLabel(details_frame, text="Phone:", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=0, sticky="w", pady=3)
        ctk.CTkLabel(details_frame, text=supplier['phone'] or "N/A", 
                    font=ctk.CTkFont(size=12),
                    text_color=XERO_GRAY).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)
        
        # Email
        ctk.CTkLabel(details_frame, text="Email:", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, sticky="w", pady=3)
        ctk.CTkLabel(details_frame, text=supplier['email'] or "N/A", 
                    font=ctk.CTkFont(size=12),
                    text_color=XERO_GRAY).grid(row=2, column=1, sticky="w", padx=(10, 0), pady=3)
        
        # State
        ctk.CTkLabel(details_frame, text="State:", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=3, column=0, sticky="w", pady=3)
        ctk.CTkLabel(details_frame, text=supplier['state'] or "N/A", 
                    font=ctk.CTkFont(size=12),
                    text_color=XERO_GRAY).grid(row=3, column=1, sticky="w", padx=(10, 0), pady=3)
        
        # Address (truncated)
        address = supplier['address'] or "N/A"
        if len(address) > 40:
            address = address[:40] + "..."
        ctk.CTkLabel(details_frame, text="Address:", 
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=4, column=0, sticky="w", pady=3)
        ctk.CTkLabel(details_frame, text=address, 
                    font=ctk.CTkFont(size=12),
                    text_color=XERO_GRAY).grid(row=4, column=1, sticky="w", padx=(10, 0), pady=3)
        

# Action buttons with Xero styling
        button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        edit_button = ctk.CTkButton(button_frame, text="Edit", 
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   fg_color=XERO_GREEN, hover_color="#059669",
                                   corner_radius=6, height=32, width=80,
                                   command=lambda s=supplier: self.edit_supplier(s))
        edit_button.pack(side="left", padx=5)
        
        delete_button = ctk.CTkButton(button_frame, text="Delete", 
                                     font=ctk.CTkFont(size=12, weight="bold"),
                                     fg_color=XERO_RED, hover_color="#DC2626",
                                     corner_radius=6, height=32, width=80,
                                     command=lambda s=supplier: self.delete_supplier(s))
        delete_button.pack(side="left", padx=5)
        
        return card_frame
        
    def edit_supplier(self, supplier):
        """Edit a supplier using the dialog"""
        # Open dialog with supplier data
        self.open_supplier_dialog()
        
        # Fill form with supplier data
        self.dialog_name_entry.insert(0, supplier['name'])
        self.dialog_gstin_entry.insert(0, supplier['gstin'] or "")
        self.dialog_address_entry.insert(0, supplier['address'] or "")
        self.dialog_phone_entry.insert(0, supplier['phone'] or "")
        self.dialog_email_entry.insert(0, supplier['email'] or "")
        self.dialog_state_entry.insert(0, supplier['state'] or "")
        
        # Change save button command to update
        self.dialog_save_button.configure(text="Update Supplier",
                                         command=lambda: self.update_supplier_from_dialog(supplier['id']))
        
    def update_supplier_from_dialog(self, supplier_id):
        """Update supplier from dialog form"""
        name = self.dialog_name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Supplier Name is required.")
            return
            
        data = (
            name,
            self.dialog_gstin_entry.get().strip(),
            self.dialog_address_entry.get().strip(),
            self.dialog_phone_entry.get().strip(),
            self.dialog_email_entry.get().strip(),
            self.dialog_state_entry.get().strip()
        )
        
        if db_manager.update_supplier(supplier_id, *data):
            messagebox.showinfo("Success", "Supplier updated successfully.")
            self.supplier_dialog.destroy()
            self.load_suppliers()
        else:
            messagebox.showerror("Database Error", "Could not update supplier.")
            
    def delete_supplier(self, supplier):
        """Delete a supplier"""
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete supplier '{supplier['name']}'?")
        if result:
            if db_manager.delete_supplier(supplier['id']):
                messagebox.showinfo("Success", "Supplier deleted successfully.")
                self.load_suppliers()
            else:
                messagebox.showerror("Database Error", "Could not delete supplier.")

    def load_suppliers_table(self, search_term=""):
        """Load suppliers into the table view"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        suppliers = db_manager.get_all_suppliers()
        
        # Filter suppliers if search term provided
        if search_term:
            suppliers = [supplier for supplier in suppliers if 
                        search_term in supplier['name'].lower() or 
                        search_term in (supplier['gstin'] or '').lower() or
                        search_term in (supplier['state'] or '').lower()]
        
        for supplier in suppliers:
            self.tree.insert("", "end", values=(
                supplier['id'], supplier['name'], supplier['gstin'] or "",
                supplier['phone'] or "", supplier['email'] or "",
                supplier['address'] or "", supplier['state'] or ""
            ))

    def get_form_data(self):
        """Get data from the form fields"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Supplier Name is required.")
            return None
        return (
            name,
            self.gstin_entry.get().strip(),
            self.address_entry.get().strip(),
            self.phone_entry.get().strip(),
            self.email_entry.get().strip(),
            self.state_entry.get().strip()
        )

    def add_supplier(self):
        """Add a new supplier"""
        data = self.get_form_data()
        if data:
            if db_manager.add_supplier(*data):
                messagebox.showinfo("Success", "Supplier added successfully.")
                self.load_suppliers()
                self.clear_form()
            else:
                messagebox.showerror("Database Error", f"Could not add supplier. '{data[0]}' may already exist.")

    def update_supplier(self):
        """Update selected supplier"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a supplier to update.")
            return

        supplier_id = self.tree.item(selected, "values")[0]
        data = self.get_form_data()
        if data:
            if db_manager.update_supplier(supplier_id, *data):
                messagebox.showinfo("Success", "Supplier updated successfully.")
                self.load_suppliers()
                self.clear_form()
            else:
                messagebox.showerror("Database Error", "Could not update supplier.")

    def clear_form(self):
        """Clear all form fields"""
        self.name_entry.delete(0, "end")
        self.gstin_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.state_entry.delete(0, "end")
        
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        
        self.update_button.configure(state="disabled")
        self.add_button.configure(state="normal")
        self.name_entry.focus()

    def on_tree_select(self, event):
        """Handle tree selection"""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.clear_form()
            
            # Fill form with selected supplier data
            self.name_entry.insert(0, values[1])
            self.gstin_entry.insert(0, values[2])
            self.phone_entry.insert(0, values[3])
            self.email_entry.insert(0, values[4])
            self.address_entry.insert(0, values[5])
            self.state_entry.insert(0, values[6])

            self.update_button.configure(state="normal")
            self.add_button.configure(state="disabled")
        else:
            self.clear_form()

    def load_suppliers(self):
        """Load suppliers based on current view"""
        if hasattr(self, 'current_view'):
            if self.current_view == "card":
                self.load_suppliers_cards()
            else:
                self.load_suppliers_table()
        else:
            # Default to card view
            self.current_view = "card"
            self.load_suppliers_cards()

    def load_data(self):
        """Public method to be called when switching to this frame"""
        self.load_suppliers()
