import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
from ui_serial_dialog import SerialEntryDialog
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

class PurchaseFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.invoice_items = []
        self.current_item_units = []
        self.create_widgets()
        self.load_data()

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
        ctk.CTkLabel(header_frame, text="Purchase Management",
                    font=ctk.CTkFont(size=32, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, sticky="w")
        
        # View toggle with Xero styling
        view_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        view_frame.grid(row=0, column=1, sticky="e")
        
        self.form_view_button = ctk.CTkButton(view_frame, text="Invoice Form",
                                             font=ctk.CTkFont(size=12, weight="bold"),
                                             fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                             corner_radius=6, height=32, width=100,
                                             command=self.show_form_view)
        self.form_view_button.pack(side="left", padx=2)
        
        self.kanban_view_button = ctk.CTkButton(view_frame, text="Kanban View",
                                               font=ctk.CTkFont(size=12, weight="bold"),
                                               fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                               text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                               corner_radius=6, height=32, width=100,
                                               command=self.show_kanban_view)
        self.kanban_view_button.pack(side="left", padx=2)
        
        # Content area with Xero styling
        content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        content_container.grid(row=1, column=0, padx=25, pady=(0, 25), sticky="nsew")
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_rowconfigure(0, weight=1)
        
        # Create both views
        self.create_form_view(content_container)
        self.create_kanban_view(content_container)
        
        # Show form view by default
        self.show_form_view()
        
    def create_form_view(self, parent):
        """Create Xero-style form view for creating purchase invoices"""
        self.form_view_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.form_view_frame.grid(row=0, column=0, sticky="nsew")
        self.form_view_frame.grid_columnconfigure(0, weight=1)
        self.form_view_frame.grid_rowconfigure(2, weight=1)
        
        # Invoice header section
        header_container = ctk.CTkFrame(self.form_view_frame, fg_color=XERO_WHITE, corner_radius=12)
        header_container.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_container.grid_columnconfigure((1, 3), weight=1)
        
        # Section title
        ctk.CTkLabel(header_container, text="Purchase Invoice Details",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, columnspan=4,
                                              padx=25, pady=(25, 20), sticky="w")
        
        # Form fields with Xero styling
        ctk.CTkLabel(header_container, text="Supplier",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=0, padx=(25, 10), pady=8, sticky="w")
        self.supplier_combo = ctk.CTkComboBox(header_container, values=[], 
                                             font=ctk.CTkFont(size=14),
                                             height=40, corner_radius=8,
                                             command=self.supplier_changed)
        self.supplier_combo.grid(row=1, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(header_container, text="Invoice Number",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        self.invoice_no_entry = ctk.CTkEntry(header_container, font=ctk.CTkFont(size=14),
                                            height=40, corner_radius=8, border_color=XERO_GRAY)
        self.invoice_no_entry.grid(row=1, column=3, padx=(0, 25), pady=8, sticky="ew")
        
        ctk.CTkLabel(header_container, text="Invoice Date",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, padx=(25, 10), pady=8, sticky="w")
        self.invoice_date_entry = ctk.CTkEntry(header_container, font=ctk.CTkFont(size=14),
                                              height=40, corner_radius=8, border_color=XERO_GRAY,
                                              placeholder_text="YYYY-MM-DD")
        self.invoice_date_entry.grid(row=2, column=1, padx=(0, 20), pady=8, sticky="ew")
        
        ctk.CTkLabel(header_container, text="Notes",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=2, padx=(0, 10), pady=8, sticky="w")
        self.notes_entry = ctk.CTkEntry(header_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY)
        self.notes_entry.grid(row=2, column=3, padx=(0, 25), pady=(8, 25), sticky="ew")
        
        # Item entry section
        item_container = ctk.CTkFrame(self.form_view_frame, fg_color=XERO_WHITE, corner_radius=12)
        item_container.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Section title
        ctk.CTkLabel(item_container, text="Add Items to Invoice",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, columnspan=6,
                                              padx=25, pady=(25, 20), sticky="w")
        
        # Item entry form with Xero styling
        ctk.CTkLabel(item_container, text="Item",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=0, padx=(25, 10), pady=8, sticky="w")
        self.item_combo = ctk.CTkComboBox(item_container, values=[], 
                                         font=ctk.CTkFont(size=14),
                                         height=40, corner_radius=8, width=200,
                                         command=self.item_changed)
        self.item_combo.grid(row=1, column=1, padx=(0, 15), pady=8, sticky="ew")
        
        ctk.CTkLabel(item_container, text="Quantity",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=2, padx=(0, 10), pady=8, sticky="w")
        self.qty_entry = ctk.CTkEntry(item_container, font=ctk.CTkFont(size=14),
                                     height=40, corner_radius=8, border_color=XERO_GRAY, width=100)
        self.qty_entry.grid(row=1, column=3, padx=(0, 15), pady=8, sticky="ew")
        
        ctk.CTkLabel(item_container, text="Unit",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=1, column=4, padx=(0, 10), pady=8, sticky="w")
        self.unit_var = ctk.StringVar()
        self.unit_option_menu = ctk.CTkOptionMenu(item_container, variable=self.unit_var, values=[],
                                                 font=ctk.CTkFont(size=14),
                                                 height=40, corner_radius=8, width=100)
        self.unit_option_menu.grid(row=1, column=5, padx=(0, 25), pady=8, sticky="ew")
        
        ctk.CTkLabel(item_container, text="Price per Unit",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=XERO_DARK_GRAY).grid(row=2, column=0, padx=(25, 10), pady=8, sticky="w")
        self.price_entry = ctk.CTkEntry(item_container, font=ctk.CTkFont(size=14),
                                       height=40, corner_radius=8, border_color=XERO_GRAY, width=120)
        self.price_entry.grid(row=2, column=1, padx=(0, 15), pady=8, sticky="ew")
        
        # Add item button
        self.add_item_button = ctk.CTkButton(item_container, text="+ Add to Invoice",
                                            font=ctk.CTkFont(size=14, weight="bold"),
                                            fg_color=XERO_GREEN, hover_color="#059669",
                                            corner_radius=8, height=40, width=150,
                                            command=self.add_item_to_invoice)
        self.add_item_button.grid(row=2, column=2, columnspan=2, padx=(0, 15), pady=(8, 25), sticky="ew")
        
        # Items table section
        table_container = ctk.CTkFrame(self.form_view_frame, fg_color=XERO_WHITE, corner_radius=12)
        table_container.grid(row=2, column=0, sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)
        
        # Table title
        ctk.CTkLabel(table_container, text="Invoice Items",
                    font=ctk.CTkFont(size=20, weight="bold"),
                    text_color=XERO_NAVY).grid(row=0, column=0, padx=25, pady=(25, 15), sticky="w")
        
        # Items treeview with modern styling
        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        tree_frame.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("item_name", "qty", "unit", "price", "gst", "total", "serials")
        self.items_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        # Configure column headings
        self.items_tree.heading("item_name", text="Item Name")
        self.items_tree.heading("qty", text="Quantity")
        self.items_tree.heading("unit", text="Unit")
        self.items_tree.heading("price", text="Price")
        self.items_tree.heading("gst", text="GST")
        self.items_tree.heading("total", text="Total")
        self.items_tree.heading("serials", text="Serial Numbers")
        
        # Configure column widths
        self.items_tree.column("item_name", width=200)
        self.items_tree.column("qty", width=80, anchor="center")
        self.items_tree.column("unit", width=80, anchor="center")
        self.items_tree.column("price", width=100, anchor="e")
        self.items_tree.column("gst", width=80, anchor="center")
        self.items_tree.column("total", width=120, anchor="e")
        self.items_tree.column("serials", width=200)
        
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.items_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Footer with total and save button
        footer_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        footer_frame.grid(row=2, column=0, padx=25, pady=(0, 25), sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)
        
        # Total display
        total_frame = ctk.CTkFrame(footer_frame, fg_color=XERO_BLUE, corner_radius=8)
        total_frame.grid(row=0, column=0, sticky="e", pady=(0, 15))
        
        self.total_label = ctk.CTkLabel(total_frame, text="Total: ₹0.00",
                                       font=ctk.CTkFont(size=18, weight="bold"),
                                       text_color=XERO_WHITE)
        self.total_label.pack(padx=20, pady=15)
        
        # Action buttons
        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="e")
        
        clear_button = ctk.CTkButton(button_frame, text="Clear All",
                                    font=ctk.CTkFont(size=14, weight="bold"),
                                    fg_color="transparent", hover_color=XERO_LIGHT_GRAY,
                                    text_color=XERO_GRAY, border_width=1, border_color=XERO_GRAY,
                                    corner_radius=8, height=40, width=120,
                                    command=self.clear_invoice)
        clear_button.pack(side="right", padx=5)
        
        self.save_button = ctk.CTkButton(button_frame, text="Save Purchase Invoice",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                        corner_radius=8, height=40, width=180,
                                        command=self.save_invoice)
        self.save_button.pack(side="right", padx=5)
        
    def create_kanban_view(self, parent):
        """Create Xero-style Kanban view for managing purchase invoices"""
        self.kanban_view_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.kanban_view_frame.grid(row=0, column=0, sticky="nsew")
        self.kanban_view_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.kanban_view_frame.grid_rowconfigure(0, weight=1)
        
        # Kanban columns with Xero styling
        self.statuses = ["Draft", "Ordered", "Received", "Paid"]
        self.status_colors = {
            "Draft": XERO_GRAY,
            "Ordered": XERO_ORANGE,
            "Received": XERO_BLUE,
            "Paid": XERO_GREEN
        }
        self.kanban_columns = {}
        
        for i, status in enumerate(self.statuses):
            column_frame = ctk.CTkFrame(self.kanban_view_frame, fg_color=XERO_WHITE, corner_radius=12)
            column_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            column_frame.grid_columnconfigure(0, weight=1)
            column_frame.grid_rowconfigure(1, weight=1)
            
            # Column header with status color
            header_frame = ctk.CTkFrame(column_frame, fg_color=self.status_colors[status], corner_radius=10)
            header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
            header_frame.grid_columnconfigure(0, weight=1)
            
            status_label = ctk.CTkLabel(header_frame, text=status,
                                       font=ctk.CTkFont(size=16, weight="bold"),
                                       text_color=XERO_WHITE)
            status_label.pack(pady=15)
            
            # Scrollable content area for invoice cards
            content_frame = ctk.CTkScrollableFrame(column_frame, fg_color="transparent", corner_radius=0)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
            content_frame.grid_columnconfigure(0, weight=1)
            
            self.kanban_columns[status] = content_frame
            
        # Load invoices into kanban
        self.populate_kanban_view()
        
    def populate_kanban_view(self):
        """Populate the Kanban view with purchase invoices"""
        # Clear existing cards
        for status in self.kanban_columns:
            for widget in self.kanban_columns[status].winfo_children():
                widget.destroy()
                
        # Sample data - in real implementation, this would come from database
        sample_invoices = [
            {"id": 1, "invoice_number": "PO-001", "supplier": "ABC Corp", "amount": 15000, "date": "2024-01-15", "status": "Draft"},
            {"id": 2, "invoice_number": "PO-002", "supplier": "XYZ Ltd", "amount": 27500, "date": "2024-01-10", "status": "Ordered"},
            {"id": 3, "invoice_number": "PO-003", "supplier": "DEF Inc", "amount": 8200, "date": "2024-01-05", "status": "Received"},
            {"id": 4, "invoice_number": "PO-004", "supplier": "GHI Co", "amount": 12800, "date": "2023-12-30", "status": "Paid"},
            {"id": 5, "invoice_number": "PO-005", "supplier": "JKL Corp", "amount": 19600, "date": "2024-01-12", "status": "Draft"},
            {"id": 6, "invoice_number": "PO-006", "supplier": "MNO Ltd", "amount": 34200, "date": "2024-01-08", "status": "Ordered"},
        ]
        
        for invoice in sample_invoices:
            self.add_invoice_to_kanban(invoice)
            
    def add_invoice_to_kanban(self, invoice):
        """Add an invoice card to the appropriate Kanban column"""
        status = invoice["status"]
        if status in self.kanban_columns:
            card_frame = ctk.CTkFrame(self.kanban_columns[status], fg_color=XERO_WHITE, corner_radius=10)
            card_frame.pack(fill="x", padx=5, pady=8)
            card_frame.grid_columnconfigure(0, weight=1)
            
            # Invoice header
            header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(15, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(header_frame, text=invoice['invoice_number'],
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=XERO_NAVY).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(header_frame, text=f"₹{invoice['amount']:,}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=self.status_colors[status]).grid(row=0, column=1, sticky="e")
            
            # Invoice details
            ctk.CTkLabel(card_frame, text=f"Supplier: {invoice['supplier']}",
                        font=ctk.CTkFont(size=12),
                        text_color=XERO_GRAY).pack(anchor="w", padx=15, pady=2)
            ctk.CTkLabel(card_frame, text=f"Date: {invoice['date']}",
                        font=ctk.CTkFont(size=12),
                        text_color=XERO_GRAY).pack(anchor="w", padx=15, pady=2)
            
            # Action buttons
            button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            button_frame.pack(fill="x", padx=15, pady=(10, 15))
            
            view_button = ctk.CTkButton(button_frame, text="View",
                                       font=ctk.CTkFont(size=11, weight="bold"),
                                       fg_color=XERO_BLUE, hover_color="#0E7A9B",
                                       corner_radius=6, height=28, width=60,
                                       command=lambda inv=invoice: self.view_invoice(inv))
            view_button.pack(side="left", padx=2)
            
            edit_button = ctk.CTkButton(button_frame, text="Edit",
                                       font=ctk.CTkFont(size=11, weight="bold"),
                                       fg_color=XERO_GREEN, hover_color="#059669",
                                       corner_radius=6, height=28, width=60,
                                       command=lambda inv=invoice: self.edit_invoice(inv))
            edit_button.pack(side="left", padx=2)
            
            if status != "Paid":
                next_status = self.get_next_status(status)
                if next_status:
                    move_button = ctk.CTkButton(button_frame, text=f"→ {next_status}",
                                               font=ctk.CTkFont(size=11, weight="bold"),
                                               fg_color=XERO_ORANGE, hover_color="#D97706",
                                               corner_radius=6, height=28, width=80,
                                               command=lambda inv=invoice, ns=next_status: self.move_invoice(inv, ns))
                    move_button.pack(side="right", padx=2)

    def get_next_status(self, current_status):
        """Get the next status in the workflow"""
        status_flow = {"Draft": "Ordered", "Ordered": "Received", "Received": "Paid"}
        return status_flow.get(current_status)
        
    def view_invoice(self, invoice):
        """View invoice details"""
        messagebox.showinfo("Invoice Details", f"Invoice: {invoice['invoice_number']}\nSupplier: {invoice['supplier']}\nAmount: ₹{invoice['amount']:,}\nStatus: {invoice['status']}")
        
    def edit_invoice(self, invoice):
        """Edit invoice (switch to form view)"""
        self.show_form_view()
        messagebox.showinfo("Edit Invoice", f"Editing invoice {invoice['invoice_number']} - Form view activated")
        
    def move_invoice(self, invoice, new_status):
        """Move invoice to next status"""
        # In real implementation, this would update the database
        invoice['status'] = new_status
        self.populate_kanban_view()
        messagebox.showinfo("Status Updated", f"Invoice {invoice['invoice_number']} moved to {new_status}")
        
    def show_form_view(self):
        """Show form view and hide Kanban view"""
        if hasattr(self, 'kanban_view_frame'):
            self.kanban_view_frame.grid_remove()
        if hasattr(self, 'form_view_frame'):
            self.form_view_frame.grid()
        
        # Update button states
        self.form_view_button.configure(fg_color=XERO_BLUE, text_color=XERO_WHITE)
        self.kanban_view_button.configure(fg_color="transparent", text_color=XERO_GRAY)
        
        self.current_view = "form"
        
    def show_kanban_view(self):
        """Show Kanban view and hide form view"""
        if hasattr(self, 'form_view_frame'):
            self.form_view_frame.grid_remove()
        if hasattr(self, 'kanban_view_frame'):
            self.kanban_view_frame.grid()
        
        # Update button states
        self.kanban_view_button.configure(fg_color=XERO_BLUE, text_color=XERO_WHITE)
        self.form_view_button.configure(fg_color="transparent", text_color=XERO_GRAY)
        
        self.current_view = "kanban"
        self.populate_kanban_view()

    def load_data(self):
        """Load data for the purchase form"""
        # Load suppliers and items
        self.suppliers = db_manager.get_all_suppliers()
        self.items = db_manager.get_all_items()
        
        if hasattr(self, 'supplier_combo'):
            self.supplier_combo.configure(values=[s['name'] for s in self.suppliers])
        
        if hasattr(self, 'item_combo'):
            # Filter for non-assembled items for the dropdown
            self.purchasable_items = [i for i in self.items if not i['is_assembled_item']]
            self.item_combo.configure(values=[i['name'] for i in self.purchasable_items])
            
        # Initialize form fields
        self.invoice_items.clear()
        self.refresh_items_tree()
        self.update_total()
        
        if hasattr(self, 'invoice_no_entry'):
            self.invoice_no_entry.delete(0, "end")
        if hasattr(self, 'invoice_date_entry'):
            self.invoice_date_entry.delete(0, "end")
            self.invoice_date_entry.insert(0, datetime.date.today().isoformat())
        if hasattr(self, 'notes_entry'):
            self.notes_entry.delete(0, "end")
            
        # Set default selections
        if hasattr(self, 'supplier_combo') and self.suppliers:
            self.supplier_combo.set(self.suppliers[0]['name'])
        if hasattr(self, 'item_combo') and hasattr(self, 'purchasable_items') and self.purchasable_items:
            self.item_combo.set(self.purchasable_items[0]['name'])
            self.item_changed()

    def supplier_changed(self, choice):
        """Handle supplier selection change"""
        pass

    def item_changed(self, choice=None):
        """Handle item selection change"""
        item_name = self.item_combo.get()
        item = next((i for i in self.purchasable_items if i['name'] == item_name), None)
        if item:
            self.price_entry.delete(0, "end")
            if item['purchase_price']:
                self.price_entry.insert(0, str(item['purchase_price']))

            # Load units for this item
            self.current_item_units = db_manager.get_units_for_item(item['id'])
            unit_names = [u['name'] for u in self.current_item_units]
            self.unit_option_menu.configure(values=unit_names)
            if unit_names:
                self.unit_var.set(unit_names[0])
            else:
                self.unit_var.set("")
                self.unit_option_menu.configure(values=[])

    def add_item_to_invoice(self):
        """Add selected item to the invoice"""
        selected_item_name = self.item_combo.get()
        qty_str = self.qty_entry.get()
        price_str = self.price_entry.get()
        selected_unit_name = self.unit_var.get()

        if not all([selected_item_name, qty_str, price_str, selected_unit_name]):
            return messagebox.showerror("Error", "Please fill all item fields, including unit.", parent=self)
        
        try:
            qty = float(qty_str)
            price = float(price_str)
        except ValueError:
            return messagebox.showerror("Error", "Quantity and Price must be numbers.", parent=self)

        item = next((i for i in self.purchasable_items if i['name'] == selected_item_name), None)
        if not item:
            return messagebox.showerror("Error", "Item not found.", parent=self)

        # Find conversion factor
        unit_info = next((u for u in self.current_item_units if u['name'] == selected_unit_name), None)
        if not unit_info:
            return messagebox.showerror("Error", "Invalid unit selected for this item.", parent=self)

        conversion_factor = unit_info['factor']
        base_quantity = qty * conversion_factor

        serials = []
        if item['is_serialized']:
            if base_quantity != int(base_quantity):
                return messagebox.showerror("Error", "Quantity for serialized items must result in a whole number of base units.", parent=self)
            dialog = SerialEntryDialog(self, int(base_quantity))
            serials = dialog.get_serials()
            if len(serials) != int(base_quantity):
                return  # User cancelled or did not enter all serials

        gst_amount = (qty * price) * (item['gst_rate'] / 100)
        self.invoice_items.append({
            "item_id": item['id'], "item_name": selected_item_name,
            "quantity": base_quantity,  # Store quantity in base unit
            "display_quantity": qty,  # For display
            "display_unit": selected_unit_name,  # For display
            "purchase_price": price / conversion_factor,  # Store price per base unit
            "display_price": price,  # For display
            "gst_rate": item['gst_rate'], "gst_amount": gst_amount,
            "serial_numbers": serials, "godown_id": 1  # Hardcoded godown for now
        })
        
        self.refresh_items_tree()
        self.update_total()
        self.qty_entry.delete(0, 'end')

    def refresh_items_tree(self):
        """Refresh the items tree display"""
        for i in self.items_tree.get_children():
            self.items_tree.delete(i)
        
        for item in self.invoice_items:
            serials_str = ", ".join(item['serial_numbers']) if item['serial_numbers'] else "N/A"
            total = (item['display_quantity'] * item['display_price']) + item['gst_amount']
            self.items_tree.insert("", "end", values=(
                item['item_name'], 
                item['display_quantity'], 
                item['display_unit'], 
                f"₹{item['display_price']:.2f}", 
                f"{item['gst_rate']}%", 
                f"₹{total:.2f}", 
                serials_str
            ))

    def update_total(self):
        """Update the total amount display"""
        total = sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items)
        self.total_label.configure(text=f"Total: ₹{total:,.2f}")

    def clear_invoice(self):
        """Clear all invoice items"""
        result = messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all items from this invoice?")
        if result:
            self.invoice_items.clear()
            self.refresh_items_tree()
            self.update_total()

    def save_invoice(self):
        """Save the purchase invoice"""
        supplier_name = self.supplier_combo.get()
        invoice_no = self.invoice_no_entry.get().strip()
        invoice_date = self.invoice_date_entry.get().strip()
        
        if not all([supplier_name, invoice_no, invoice_date]):
            return messagebox.showerror("Error", "Supplier, Invoice Number, and Date are required.", parent=self)
        
        if not self.invoice_items:
            return messagebox.showerror("Error", "Please add at least one item to the invoice.", parent=self)

        supplier = next((s for s in self.suppliers if s['name'] == supplier_name), None)
        if not supplier:
            return messagebox.showerror("Error", "Invalid supplier selected.", parent=self)

        total_amount = sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items)
        total_gst = sum(i['gst_amount'] for i in self.invoice_items)

        invoice_data = {
            "supplier_id": supplier['id'], 
            "invoice_number": invoice_no, 
            "invoice_date": invoice_date,
            "total_amount": total_amount, 
            "gst_amount": total_gst,
            "notes": self.notes_entry.get().strip()
        }

        # The backend expects quantity and price per base unit
        invoice_id = db_manager.create_purchase_invoice_transaction(invoice_data, self.invoice_items)

        if invoice_id:
            messagebox.showinfo("Success", f"Purchase Invoice #{invoice_id} saved successfully.", parent=self)
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to save invoice. Check logs for details.", parent=self)

    def load_data_public(self):
        """Public method to be called when switching to this frame"""
        self.load_data()
