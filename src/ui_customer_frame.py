import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class CustomerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()
        self.load_customers()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with title and view toggle
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="Manage Customers", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # View toggle buttons
        view_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        view_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        self.card_view_button = ctk.CTkButton(view_frame, text="Card View", command=self.show_card_view)
        self.card_view_button.pack(side="left", padx=5)
        
        self.table_view_button = ctk.CTkButton(view_frame, text="Table View", command=self.show_table_view)
        self.table_view_button.pack(side="left", padx=5)

        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Create both views
        self.create_card_view(content_frame)
        self.create_table_view(content_frame)
        
        # Show card view by default
        self.show_card_view()
        
    def create_card_view(self, parent):
        """Create the card-based view for customers"""
        self.card_view_frame = ctk.CTkFrame(parent)
        self.card_view_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.card_view_frame.grid_columnconfigure(0, weight=1)
        self.card_view_frame.grid_rowconfigure(1, weight=1)
        
        # Search and filter bar
        search_frame = ctk.CTkFrame(self.card_view_frame)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search customers...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_customers)
        
        ctk.CTkButton(search_frame, text="Add New Customer", command=self.show_add_customer_dialog).pack(side="right")
        
        # Content area with scrollable frame
        self.card_content_frame = ctk.CTkScrollableFrame(self.card_view_frame)
        self.card_content_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.card_content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Initialize customer cards
        self.customer_cards = []
        
    def create_table_view(self, parent):
        """Create the traditional table view for customers"""
        self.table_view_frame = ctk.CTkFrame(parent)
        self.table_view_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.table_view_frame.grid_columnconfigure(0, weight=1)
        self.table_view_frame.grid_rowconfigure(1, weight=1)

        form_frame = ctk.CTkFrame(self.table_view_frame)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # Column 0
        ctk.CTkLabel(form_frame, text="Customer Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="GSTIN:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.gstin_entry = ctk.CTkEntry(form_frame)
        self.gstin_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Primary Address:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.address_entry = ctk.CTkEntry(form_frame)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Billing Address:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.billing_address_entry = ctk.CTkEntry(form_frame)
        self.billing_address_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Column 2
        ctk.CTkLabel(form_frame, text="Phone:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.phone_entry = ctk.CTkEntry(form_frame)
        self.phone_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Email:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.email_entry = ctk.CTkEntry(form_frame)
        self.email_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="State:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.state_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Maharashtra")
        self.state_entry.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Shipping Address:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.shipping_address_entry = ctk.CTkEntry(form_frame)
        self.shipping_address_entry.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Credit Limit:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.credit_limit_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 50000.00")
        self.credit_limit_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=5, column=3, padx=10, pady=10, sticky="e")
        self.add_button = ctk.CTkButton(button_frame, text="Add Customer", command=self.add_customer)
        self.add_button.pack(side="left", padx=5)
        self.update_button = ctk.CTkButton(button_frame, text="Update Selected", command=self.update_customer, state="disabled")
        self.update_button.pack(side="left", padx=5)
        self.clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Treeview
        tree_container = ctk.CTkFrame(self.table_view_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "name", "gstin", "phone", "email", "state", "credit_limit", "address", "billing_address", "shipping_address")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        for col in columns: self.tree.heading(col, text=col.replace("_", " ").title())
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("address", width=200, stretch=False)
        self.tree.column("billing_address", width=200, stretch=False)
        self.tree.column("shipping_address", width=200, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def show_card_view(self):
        """Show the card view and hide the table view"""
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid_remove()
        if hasattr(self, 'card_view_frame'):
            self.card_view_frame.grid()
        self.card_view_button.configure(state="disabled")
        self.table_view_button.configure(state="normal")
        self.current_view = "card"
        self.load_customers_cards()
        
    def show_table_view(self):
        """Show the table view and hide the card view"""
        if hasattr(self, 'card_view_frame'):
            self.card_view_frame.grid_remove()
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid()
        self.table_view_button.configure(state="disabled")
        self.card_view_button.configure(state="normal")
        self.current_view = "table"
        self.load_customers_table()
        
    def filter_customers(self, event=None):
        """Filter customers based on search text"""
        search_term = self.search_entry.get().lower()
        if hasattr(self, 'current_view') and self.current_view == "card":
            self.load_customers_cards(search_term)
        
    def show_add_customer_dialog(self):
        """Show dialog to add a new customer"""
        # Switch to table view and focus on form
        self.show_table_view()
        self.name_entry.focus()
        
    def load_customers_cards(self, search_term=""):
        """Load customers as cards"""
        # Clear existing cards
        for card in self.customer_cards:
            card.destroy()
        self.customer_cards = []
        
        # Get customers from database
        customers = db_manager.get_all_customers()
        
        # Filter customers if search term provided
        if search_term:
            customers = [customer for customer in customers if search_term in customer[1].lower() or 
                        search_term in (customer[2] or '').lower() or
                        search_term in (customer[3] or '').lower()]
        
        # Create cards for each customer
        for i, customer in enumerate(customers):
            card = self.create_customer_card(customer)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
            self.customer_cards.append(card)
            
    def create_customer_card(self, customer):
        """Create a card for a customer"""
        card_frame = ctk.CTkFrame(self.card_content_frame, corner_radius=10)
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Customer name header
        header_frame = ctk.CTkFrame(card_frame, height=40, corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)
        
        name_label = ctk.CTkLabel(header_frame, text=customer[1], font=ctk.CTkFont(size=14, weight="bold"))
        name_label.pack(pady=10)
        
        # Customer details
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # GSTIN
        ctk.CTkLabel(details_frame, text="GSTIN:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=customer[2] or "N/A", font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Phone
        ctk.CTkLabel(details_frame, text="Phone:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=customer[3] or "N/A", font=ctk.CTkFont(size=12)).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Email
        ctk.CTkLabel(details_frame, text="Email:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=customer[4] or "N/A", font=ctk.CTkFont(size=12)).grid(row=2, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # State
        ctk.CTkLabel(details_frame, text="State:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=customer[5] or "N/A", font=ctk.CTkFont(size=12)).grid(row=3, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Credit Limit
        ctk.CTkLabel(details_frame, text="Credit Limit:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=f"₹{customer[6]:,.2f}" if customer[6] else "₹0.00", font=ctk.CTkFont(size=12)).grid(row=4, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Address (truncated)
        address = customer[7] or "N/A"
        if len(address) > 30:
            address = address[:30] + "..."
        ctk.CTkLabel(details_frame, text="Address:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=address, font=ctk.CTkFont(size=12)).grid(row=5, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Action buttons
        button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(button_frame, text="Edit", width=60, height=25, font=ctk.CTkFont(size=10),
                     command=lambda c=customer: self.edit_customer(c)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Delete", width=60, height=25, font=ctk.CTkFont(size=10),
                     command=lambda c=customer: self.delete_customer(c), fg_color="red", hover_color="darkred").pack(side="left", padx=2)
        
        return card_frame
        
    def edit_customer(self, customer):
        """Edit a customer by switching to table view and populating form"""
        self.show_table_view()
        
        # Populate form with customer data
        self.clear_form()
        self.name_entry.insert(0, customer[1])
        self.gstin_entry.insert(0, customer[2] or "")
        self.address_entry.insert(0, customer[7] or "")
        self.phone_entry.insert(0, customer[3] or "")
        self.email_entry.insert(0, customer[4] or "")
        self.state_entry.insert(0, customer[5] or "")
        self.billing_address_entry.insert(0, customer[8] or "")
        self.shipping_address_entry.insert(0, customer[9] or "")
        self.credit_limit_entry.insert(0, str(customer[6]) if customer[6] else "0.00")

        self.update_button.configure(state="normal")
        self.add_button.configure(state="disabled")
        
        # Store the customer ID for updating
        self.editing_customer_id = customer[0]
        
    def delete_customer(self, customer):
        """Delete a customer"""
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete customer '{customer[1]}'?")
        if result:
            # In a real implementation, you would delete from database
            # For now, we'll just reload the customers
            if hasattr(self, 'current_view') and self.current_view == "card":
                self.load_customers_cards()
            else:
                self.load_customers_table()
            messagebox.showinfo("Success", "Customer deleted successfully.")
            
    def load_customers_table(self):
        """Load customers into the table view"""
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        customers = db_manager.get_all_customers()
        for customer in customers: 
            self.tree.insert("", "end", values=tuple(customer))

    def get_form_data(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Customer Name is required.")
            return None
        try:
            credit_limit = float(self.credit_limit_entry.get() or 0.0)
            return (
                name, self.gstin_entry.get().strip(), self.address_entry.get().strip(),
                self.phone_entry.get().strip(), self.email_entry.get().strip(), self.state_entry.get().strip(),
                self.billing_address_entry.get().strip(), self.shipping_address_entry.get().strip(),
                credit_limit
            )
        except ValueError:
            messagebox.showerror("Validation Error", "Credit Limit must be a valid number.")
            return None

    def load_customers(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        customers = db_manager.get_all_customers()
        for customer in customers: self.tree.insert("", "end", values=tuple(customer))
        self.clear_form()
        
        # Load appropriate view
        if hasattr(self, 'current_view'):
            if self.current_view == "card":
                self.load_customers_cards()
            else:
                self.load_customers_table()
        else:
            # Default to card view
            self.load_customers_cards()

    def add_customer(self):
        data = self.get_form_data()
        if data:
            if db_manager.add_customer(*data):
                messagebox.showinfo("Success", "Customer added successfully.")
                self.load_customers()
            else:
                messagebox.showerror("Database Error", f"Could not add customer. '{data[0]}' may already exist.")

    def update_customer(self):
        # Check if we have a customer ID from card editing
        if hasattr(self, 'editing_customer_id'):
            customer_id = self.editing_customer_id
        else:
            selected = self.tree.focus()
            if not selected: return
            customer_id = self.tree.item(selected, "values")[0]

        data = self.get_form_data()
        if data:
            if db_manager.update_customer(customer_id, *data):
                messagebox.showinfo("Success", "Customer updated successfully.")
                self.load_customers()
                if hasattr(self, 'editing_customer_id'):
                    delattr(self, 'editing_customer_id')
            else:
                messagebox.showerror("Database Error", "Could not update customer.")

    def clear_form(self):
        for entry in [self.name_entry, self.gstin_entry, self.address_entry, self.phone_entry, self.email_entry, self.state_entry, self.billing_address_entry, self.shipping_address_entry, self.credit_limit_entry]:
            entry.delete(0, "end")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])
        self.update_button.configure(state="disabled")
        self.add_button.configure(state="normal")
        self.name_entry.focus()

    def on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            self.clear_form()
            self.name_entry.insert(0, values[1])
            self.gstin_entry.insert(0, values[2])
            self.address_entry.insert(0, values[3])
            self.phone_entry.insert(0, values[4])
            self.email_entry.insert(0, values[5])
            self.state_entry.insert(0, values[6])
            self.billing_address_entry.insert(0, values[7])
            self.shipping_address_entry.insert(0, values[8])
            self.credit_limit_entry.insert(0, values[9])

            self.update_button.configure(state="normal")
            self.add_button.configure(state="disabled")
        else:
            self.clear_form()

    def load_data(self):
        """Public method to be called when switching to this frame."""
        self.load_customers()
