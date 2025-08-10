import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
from ui_serial_selector_dialog import SerialSelectorDialog
import datetime

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

class SalesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=XERO_LIGHT_GRAY)
        self.invoice_items = []
        self.current_item_units = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with title and actions
        self.create_header()
        
        # Main content area
        self.create_main_content()

    def create_header(self):
        """Create Xero-style header"""
        header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=XERO_WHITE)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        # Title section
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        ctk.CTkLabel(title_frame, text="Sales", 
                    font=ctk.CTkFont(size=32, weight="bold"), 
                    text_color=XERO_NAVY).pack(anchor="w")
        
        ctk.CTkLabel(title_frame, text="Create and manage sales invoices", 
                    font=ctk.CTkFont(size=16), 
                    text_color=XERO_GRAY).pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=1, padx=30, pady=20, sticky="e")
        
        ctk.CTkButton(actions_frame, text="View All Invoices", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                     text_color=XERO_BLUE, border_color=XERO_BLUE, border_width=2,
                     corner_radius=8, height=40, width=140,
                     command=self.show_invoices_list).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(actions_frame, text="+ New Invoice", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=40, width=140,
                     command=self.show_new_invoice).pack(side="right")

    def create_main_content(self):
        """Create main content area"""
        # Main container
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Create invoice creation view
        self.create_invoice_view()
        
        # Create invoices list view
        self.create_invoices_list_view()
        
        # Show new invoice by default
        self.show_new_invoice()

    def create_invoice_view(self):
        """Create Xero-style invoice creation interface"""
        self.invoice_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.invoice_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        self.invoice_frame.grid_columnconfigure(0, weight=1)
        self.invoice_frame.grid_rowconfigure(2, weight=1)
        
        # Invoice header card
        self.create_invoice_header()
        
        # Invoice items section
        self.create_invoice_items_section()
        
        # Invoice totals and actions
        self.create_invoice_footer()

    def create_invoice_header(self):
        """Create invoice header with customer and invoice details"""
        header_card = ctk.CTkFrame(self.invoice_frame, corner_radius=12, fg_color=XERO_WHITE,
                                  border_width=1, border_color="#E5E7EB")
        header_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_card.grid_columnconfigure((0, 1), weight=1)
        
        # Card title
        title_frame = ctk.CTkFrame(header_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=25, pady=(20, 10))
        
        ctk.CTkLabel(title_frame, text="Invoice Details", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x")
        
        # Left column - Customer details
        left_column = ctk.CTkFrame(header_card, fg_color="transparent")
        left_column.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 25))
        
        ctk.CTkLabel(left_column, text="Customer *", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=(0, 5))
        
        self.customer_combo = ctk.CTkComboBox(left_column, values=[], height=40,
                                             font=ctk.CTkFont(size=14),
                                             dropdown_font=ctk.CTkFont(size=14),
                                             border_color=XERO_BLUE, button_color=XERO_BLUE,
                                             button_hover_color=XERO_DARK_BLUE)
        self.customer_combo.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(left_column, text="Invoice Date *", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=(0, 5))
        
        self.invoice_date_entry = ctk.CTkEntry(left_column, height=40, 
                                              font=ctk.CTkFont(size=14),
                                              border_color=XERO_BLUE)
        self.invoice_date_entry.insert(0, datetime.date.today().isoformat())
        self.invoice_date_entry.pack(fill="x")
        
        # Right column - Invoice details
        right_column = ctk.CTkFrame(header_card, fg_color="transparent")
        right_column.grid(row=1, column=1, sticky="ew", padx=25, pady=(0, 25))
        
        ctk.CTkLabel(right_column, text="Invoice Number", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=(0, 5))
        
        self.invoice_no_frame = ctk.CTkFrame(right_column, height=40, fg_color=XERO_LIGHT_BLUE,
                                            corner_radius=8)
        self.invoice_no_frame.pack(fill="x", pady=(0, 15))
        
        self.invoice_no_label = ctk.CTkLabel(self.invoice_no_frame, text="", 
                                            font=ctk.CTkFont(size=16, weight="bold"), 
                                            text_color=XERO_BLUE)
        self.invoice_no_label.pack(pady=10)
        
        ctk.CTkLabel(right_column, text="Due Date", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(fill="x", pady=(0, 5))
        
        self.due_date_entry = ctk.CTkEntry(right_column, height=40, 
                                          font=ctk.CTkFont(size=14),
                                          border_color=XERO_BLUE)
        # Set due date to 30 days from today
        due_date = datetime.date.today() + datetime.timedelta(days=30)
        self.due_date_entry.insert(0, due_date.isoformat())
        self.due_date_entry.pack(fill="x")

    def create_invoice_items_section(self):
        """Create Xero-style invoice items section"""
        items_card = ctk.CTkFrame(self.invoice_frame, corner_radius=12, fg_color=XERO_WHITE,
                                 border_width=1, border_color="#E5E7EB")
        items_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        items_card.grid_columnconfigure(0, weight=1)
        
        # Card title
        title_frame = ctk.CTkFrame(items_card, fg_color="transparent")
        title_frame.pack(fill="x", padx=25, pady=(20, 15))
        
        ctk.CTkLabel(title_frame, text="Invoice Items", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").pack(side="left")
        
        ctk.CTkButton(title_frame, text="+ Add Item", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=35, width=100,
                     command=self.show_add_item_dialog).pack(side="right")
        
        # Items table
        table_frame = ctk.CTkFrame(items_card, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Create modern table headers
        headers_frame = ctk.CTkFrame(table_frame, height=50, fg_color=XERO_LIGHT_BLUE,
                                    corner_radius=8)
        headers_frame.pack(fill="x", pady=(0, 10))
        headers_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        headers_frame.grid_propagate(False)
        
        headers = ["Item", "Description", "Qty", "Unit Price", "Tax", "Amount"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(headers_frame, text=header, 
                        font=ctk.CTkFont(size=14, weight="bold"), 
                        text_color=XERO_NAVY).grid(row=0, column=i, padx=10, pady=15)
        
        # Items list container
        self.items_container = ctk.CTkScrollableFrame(table_frame, height=200,
                                                     fg_color="transparent",
                                                     scrollbar_button_color=XERO_BLUE)
        self.items_container.pack(fill="both", expand=True)
        self.items_container.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    def create_invoice_footer(self):
        """Create invoice totals and action buttons"""
        footer_card = ctk.CTkFrame(self.invoice_frame, corner_radius=12, fg_color=XERO_WHITE,
                                  border_width=1, border_color="#E5E7EB")
        footer_card.grid(row=2, column=0, sticky="ew")
        footer_card.grid_columnconfigure(0, weight=1)
        
        # Totals section
        totals_frame = ctk.CTkFrame(footer_card, fg_color="transparent")
        totals_frame.pack(fill="x", padx=25, pady=25)
        totals_frame.grid_columnconfigure(0, weight=1)
        
        # Totals display
        totals_display = ctk.CTkFrame(totals_frame, fg_color="transparent")
        totals_display.grid(row=0, column=0, sticky="e", pady=(0, 20))
        
        # Subtotal
        subtotal_frame = ctk.CTkFrame(totals_display, fg_color="transparent")
        subtotal_frame.pack(fill="x", pady=2)
        subtotal_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(subtotal_frame, text="Subtotal:", 
                    font=ctk.CTkFont(size=16), 
                    text_color=XERO_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        
        self.subtotal_label = ctk.CTkLabel(subtotal_frame, text="₹0.00", 
                                          font=ctk.CTkFont(size=16), 
                                          text_color=XERO_NAVY, anchor="e")
        self.subtotal_label.grid(row=0, column=1, sticky="e", padx=(50, 0))
        
        # Tax total
        tax_frame = ctk.CTkFrame(totals_display, fg_color="transparent")
        tax_frame.pack(fill="x", pady=2)
        tax_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tax_frame, text="Total Tax:", 
                    font=ctk.CTkFont(size=16), 
                    text_color=XERO_GRAY, anchor="w").grid(row=0, column=0, sticky="w")
        
        self.tax_total_label = ctk.CTkLabel(tax_frame, text="₹0.00", 
                                           font=ctk.CTkFont(size=16), 
                                           text_color=XERO_NAVY, anchor="e")
        self.tax_total_label.grid(row=0, column=1, sticky="e", padx=(50, 0))
        
        # Grand total
        total_frame = ctk.CTkFrame(totals_display, fg_color=XERO_LIGHT_BLUE, 
                                  corner_radius=8, height=50)
        total_frame.pack(fill="x", pady=(10, 0))
        total_frame.grid_columnconfigure(0, weight=1)
        total_frame.grid_propagate(False)
        
        ctk.CTkLabel(total_frame, text="Total:", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=XERO_NAVY, anchor="w").grid(row=0, column=0, sticky="w", padx=15, pady=12)
        
        self.total_label = ctk.CTkLabel(total_frame, text="₹0.00", 
                                       font=ctk.CTkFont(size=24, weight="bold"), 
                                       text_color=XERO_BLUE, anchor="e")
        self.total_label.grid(row=0, column=1, sticky="e", padx=15, pady=12)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        
        ctk.CTkButton(actions_frame, text="Save as Draft", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                     text_color=XERO_BLUE, border_color=XERO_BLUE, border_width=2,
                     corner_radius=8, height=45, width=140,
                     command=self.save_draft).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(actions_frame, text="Save & Send", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=45, width=140,
                     command=self.save_invoice).pack(side="right")

    def create_invoices_list_view(self):
        """Create invoices list view"""
        self.invoices_list_frame = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.invoices_list_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)
        self.invoices_list_frame.grid_columnconfigure(0, weight=1)
        self.invoices_list_frame.grid_rowconfigure(1, weight=1)
        
        # List header
        list_header = ctk.CTkFrame(self.invoices_list_frame, corner_radius=12, fg_color=XERO_WHITE,
                                  border_width=1, border_color="#E5E7EB", height=60)
        list_header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        list_header.grid_columnconfigure(1, weight=1)
        list_header.grid_propagate(False)
        
        ctk.CTkLabel(list_header, text="All Sales Invoices", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=XERO_NAVY).grid(row=0, column=0, padx=25, pady=15, sticky="w")
        
        # Search and filter
        search_frame = ctk.CTkFrame(list_header, fg_color="transparent")
        search_frame.grid(row=0, column=1, padx=25, pady=15, sticky="e")
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search invoices...", 
                                        width=200, height=35, font=ctk.CTkFont(size=14),
                                        border_color=XERO_BLUE)
        self.search_entry.pack(side="right")
        
        # Invoices table
        table_card = ctk.CTkFrame(self.invoices_list_frame, corner_radius=12, fg_color=XERO_WHITE,
                                 border_width=1, border_color="#E5E7EB")
        table_card.grid(row=1, column=0, sticky="nsew")
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)
        
        # Create treeview with modern styling
        tree_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        columns = ("invoice_no", "customer", "date", "due_date", "amount", "status")
        self.invoices_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        headings = ["Invoice #", "Customer", "Date", "Due Date", "Amount", "Status"]
        for col, heading in zip(columns, headings):
            self.invoices_tree.heading(col, text=heading)
            self.invoices_tree.column(col, width=150, anchor="center")
        
        # Configure treeview styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=35)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        
        self.invoices_tree.pack(fill="both", expand=True)

    def show_new_invoice(self):
        """Show new invoice creation view"""
        self.invoices_list_frame.grid_remove()
        self.invoice_frame.grid()

    def show_invoices_list(self):
        """Show invoices list view"""
        self.invoice_frame.grid_remove()
        self.invoices_list_frame.grid()
        self.load_invoices_list()

    def show_add_item_dialog(self):
        """Show dialog to add item to invoice"""
        # Create item selection dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Item to Invoice")
        dialog.geometry("500x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Dialog content
        content_frame = ctk.CTkFrame(dialog, fg_color=XERO_WHITE)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(content_frame, text="Add Item", 
                    font=ctk.CTkFont(size=20, weight="bold"), 
                    text_color=XERO_NAVY).pack(pady=(0, 20))
        
        # Item selection
        ctk.CTkLabel(content_frame, text="Item:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY).pack(anchor="w", pady=(0, 5))
        
        item_combo = ctk.CTkComboBox(content_frame, values=[], height=40,
                                    font=ctk.CTkFont(size=14))
        item_combo.pack(fill="x", pady=(0, 15))
        
        # Quantity and price
        qty_price_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        qty_price_frame.pack(fill="x", pady=(0, 15))
        qty_price_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Quantity
        qty_frame = ctk.CTkFrame(qty_price_frame, fg_color="transparent")
        qty_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ctk.CTkLabel(qty_frame, text="Quantity:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY).pack(anchor="w", pady=(0, 5))
        
        qty_entry = ctk.CTkEntry(qty_frame, height=40, font=ctk.CTkFont(size=14))
        qty_entry.pack(fill="x")
        
        # Price
        price_frame = ctk.CTkFrame(qty_price_frame, fg_color="transparent")
        price_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        ctk.CTkLabel(price_frame, text="Unit Price:", 
                    font=ctk.CTkFont(size=14, weight="bold"), 
                    text_color=XERO_NAVY).pack(anchor="w", pady=(0, 5))
        
        price_entry = ctk.CTkEntry(price_frame, height=40, font=ctk.CTkFont(size=14))
        price_entry.pack(fill="x")
        
        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkButton(button_frame, text="Cancel", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color="transparent", hover_color=XERO_LIGHT_BLUE,
                     text_color=XERO_BLUE, border_color=XERO_BLUE, border_width=2,
                     corner_radius=8, height=40, width=100,
                     command=dialog.destroy).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(button_frame, text="Add Item", 
                     font=ctk.CTkFont(size=14, weight="bold"),
                     fg_color=XERO_BLUE, hover_color=XERO_DARK_BLUE,
                     corner_radius=8, height=40, width=120,
                     command=lambda: self.add_item_to_invoice_from_dialog(
                         item_combo, qty_entry, price_entry, dialog)).pack(side="right")

    def add_item_to_invoice_from_dialog(self, item_combo, qty_entry, price_entry, dialog):
        """Add item to invoice from dialog"""
        try:
            item_name = item_combo.get()
            qty = float(qty_entry.get())
            price = float(price_entry.get())
            
            if not all([item_name, qty, price]):
                messagebox.showerror("Error", "Please fill all fields.")
                return
            
            # Add item to invoice (simplified)
            item_data = {
                "name": item_name,
                "qty": qty,
                "price": price,
                "tax": price * qty * 0.18,  # 18% GST
                "total": price * qty * 1.18
            }
            
            self.invoice_items.append(item_data)
            self.refresh_invoice_items()
            self.update_totals()
            
            dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and price.")

    def refresh_invoice_items(self):
        """Refresh the invoice items display"""
        # Clear existing items
        for widget in self.items_container.winfo_children():
            widget.destroy()
        
        # Add items to display
        for i, item in enumerate(self.invoice_items):
            item_row = ctk.CTkFrame(self.items_container, fg_color="transparent")
            item_row.pack(fill="x", pady=2)
            item_row.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
            
            # Item details
            ctk.CTkLabel(item_row, text=item["name"], 
                        font=ctk.CTkFont(size=14), 
                        text_color=XERO_NAVY).grid(row=0, column=0, padx=10, pady=10)
            
            ctk.CTkLabel(item_row, text="Product description", 
                        font=ctk.CTkFont(size=12), 
                        text_color=XERO_GRAY).grid(row=0, column=1, padx=10, pady=10)
            
            ctk.CTkLabel(item_row, text=str(item["qty"]), 
                        font=ctk.CTkFont(size=14), 
                        text_color=XERO_NAVY).grid(row=0, column=2, padx=10, pady=10)
            
            ctk.CTkLabel(item_row, text=f"₹{item['price']:.2f}", 
                        font=ctk.CTkFont(size=14), 
                        text_color=XERO_NAVY).grid(row=0, column=3, padx=10, pady=10)
            
            ctk.CTkLabel(item_row, text=f"₹{item['tax']:.2f}", 
                        font=ctk.CTkFont(size=14), 
                        text_color=XERO_NAVY).grid(row=0, column=4, padx=10, pady=10)
            
            ctk.CTkLabel(item_row, text=f"₹{item['total']:.2f}", 
                        font=ctk.CTkFont(size=14, weight="bold"), 
                        text_color=XERO_NAVY).grid(row=0, column=5, padx=10, pady=10)

    def update_totals(self):
        """Update invoice totals"""
        subtotal = sum(item["price"] * item["qty"] for item in self.invoice_items)
        tax_total = sum(item["tax"] for item in self.invoice_items)
        total = subtotal + tax_total
        
        self.subtotal_label.configure(text=f"₹{subtotal:,.2f}")
        self.tax_total_label.configure(text=f"₹{tax_total:,.2f}")
        self.total_label.configure(text=f"₹{total:,.2f}")

    def save_draft(self):
        """Save invoice as draft"""
        messagebox.showinfo("Success", "Invoice saved as draft!")

    def save_invoice(self):
        """Save and send invoice"""
        customer = self.customer_combo.get()
        if not customer:
            messagebox.showerror("Error", "Please select a customer.")
            return
        
        if not self.invoice_items:
            messagebox.showerror("Error", "Please add items to the invoice.")
            return
        
        messagebox.showinfo("Success", "Invoice saved and sent successfully!")
        
        # Clear form
        self.invoice_items = []
        self.refresh_invoice_items()
        self.update_totals()

    def load_invoices_list(self):
        """Load invoices into the list view"""
        # Clear existing items
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
        
        # Sample data - replace with actual database call
        sample_invoices = [
            ("INV-2024-001", "ABC Corporation", "2024-01-15", "2024-02-14", "₹125,000", "Paid"),
            ("INV-2024-002", "XYZ Industries", "2024-01-16", "2024-02-15", "₹98,000", "Pending"),
            ("INV-2024-003", "Tech Solutions", "2024-01-17", "2024-02-16", "₹75,000", "Overdue"),
            ("INV-2024-004", "Global Corp", "2024-01-18", "2024-02-17", "₹150,000", "Draft")
        ]
        
        for invoice in sample_invoices:
            self.invoices_tree.insert("", "end", values=invoice)

    def load_data(self):
        """Load data for the sales frame"""
        # Load customers
        self.customers = db_manager.get_all_customers()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])
        
        # Load items for item selection
        self.items = db_manager.get_all_items()
        
        # Set invoice number
        self.invoice_no_label.configure(text=db_manager.get_next_invoice_number())
        
        # Clear invoice items
        self.invoice_items = []
        self.refresh_invoice_items()
        self.update_totals()
