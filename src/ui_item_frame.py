import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager

class ItemFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.unit_map = {}
        self.hsn_map = {}
        self.gst_slab_map = {}
        self.hsn_data = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header with title and view toggle
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="Manage Product Items", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
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
        """Create the card-based view for items"""
        self.card_view_frame = ctk.CTkFrame(parent)
        self.card_view_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.card_view_frame.grid_columnconfigure(0, weight=1)
        self.card_view_frame.grid_rowconfigure(1, weight=1)
        
        # Search and filter bar
        search_frame = ctk.CTkFrame(self.card_view_frame)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search items...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_items)
        
        ctk.CTkButton(search_frame, text="Add New Item", command=self.show_add_item_dialog).pack(side="right")
        
        # Content area with scrollable frame
        self.card_content_frame = ctk.CTkScrollableFrame(self.card_view_frame)
        self.card_content_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.card_content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Initialize item cards
        self.item_cards = []
        
    def create_table_view(self, parent):
        """Create the traditional table view for items"""
        self.table_view_frame = ctk.CTkFrame(parent)
        self.table_view_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.table_view_frame.grid_columnconfigure(0, weight=1)
        self.table_view_frame.grid_rowconfigure(1, weight=1)

        form_frame = ctk.CTkFrame(self.table_view_frame)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

        # --- Form Fields ---
        ctk.CTkLabel(form_frame, text="Item Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Intel i5-13400F CPU")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="HSN/SAC Code:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.hsn_var = ctk.StringVar()
        self.hsn_option_menu = ctk.CTkOptionMenu(form_frame, variable=self.hsn_var, values=[], command=self.on_hsn_select_in_form)
        self.hsn_option_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="GST Slab:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.gst_var = ctk.StringVar()
        self.gst_option_menu = ctk.CTkOptionMenu(form_frame, variable=self.gst_var, values=[])
        self.gst_option_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Purchase Price:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.purchase_price_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 15000.00")
        self.purchase_price_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Base Unit:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.unit_var = ctk.StringVar()
        self.unit_option_menu = ctk.CTkOptionMenu(form_frame, variable=self.unit_var, values=[])
        self.unit_option_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Selling Price:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.selling_price_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 18500.00")
        self.selling_price_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Warranty (Months):").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.warranty_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 36")
        self.warranty_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Min. Stock Level:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.min_stock_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., 5")
        self.min_stock_entry.grid(row=2, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Category:").grid(row=3, column=2, padx=10, pady=5, sticky="w")
        self.category_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., CPU, RAM")
        self.category_entry.grid(row=3, column=3, padx=10, pady=5, sticky="ew")

        # --- Buttons ---
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky="e")
        self.add_button = ctk.CTkButton(button_frame, text="Add Item", command=self.add_item)
        self.add_button.pack(side="left", padx=5)
        self.update_button = ctk.CTkButton(button_frame, text="Update Selected", command=self.update_item, state="disabled")
        self.update_button.pack(side="left", padx=5)
        self.clear_button = ctk.CTkButton(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # --- Treeview ---
        tree_container = ctk.CTkFrame(self.table_view_frame)
        tree_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("id", "name", "category", "unit", "hsn", "gst", "purchase", "selling", "warranty", "min_stock")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings")
        # ... (headings and columns setup is the same)
        self.tree.heading("id", text="ID"); self.tree.heading("name", text="Name"); self.tree.heading("category", text="Category"); self.tree.heading("unit", text="Unit"); self.tree.heading("hsn", text="HSN"); self.tree.heading("gst", text="GST %"); self.tree.heading("purchase", text="Purchase Price"); self.tree.heading("selling", text="Selling Price"); self.tree.heading("warranty", text="Warranty"); self.tree.heading("min_stock", text="Min. Stock")
        for col in columns: self.tree.column(col, width=100, anchor="w")
        self.tree.column("id", width=40, anchor="center"); self.tree.column("name", width=200); self.tree.column("unit", width=60)
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
        self.load_items_cards()
        
    def show_table_view(self):
        """Show the table view and hide the card view"""
        if hasattr(self, 'card_view_frame'):
            self.card_view_frame.grid_remove()
        if hasattr(self, 'table_view_frame'):
            self.table_view_frame.grid()
        self.table_view_button.configure(state="disabled")
        self.card_view_button.configure(state="normal")
        self.current_view = "table"
        self.load_items_table()
        
    def filter_items(self, event=None):
        """Filter items based on search text"""
        search_term = self.search_entry.get().lower()
        if hasattr(self, 'current_view') and self.current_view == "card":
            self.load_items_cards(search_term)
        
    def show_add_item_dialog(self):
        """Show dialog to add a new item"""
        # Switch to table view and focus on form
        self.show_table_view()
        self.name_entry.focus()
        
    def load_items_cards(self, search_term=""):
        """Load items as cards"""
        # Clear existing cards
        for card in self.item_cards:
            card.destroy()
        self.item_cards = []
        
        # Get items from database
        items = db_manager.get_all_items()
        
        # Filter items if search term provided
        if search_term:
            items = [item for item in items if search_term in item['name'].lower() or 
                    search_term in (item['category'] or '').lower()]
        
        # Create cards for each item
        for i, item in enumerate(items):
            card = self.create_item_card(item)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="ew")
            self.item_cards.append(card)
            
    def create_item_card(self, item):
        """Create a card for an item"""
        card_frame = ctk.CTkFrame(self.card_content_frame, corner_radius=10)
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Item name header
        header_frame = ctk.CTkFrame(card_frame, height=40, corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)
        
        name_label = ctk.CTkLabel(header_frame, text=item['name'], font=ctk.CTkFont(size=14, weight="bold"))
        name_label.pack(pady=10)
        
        # Item details
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Category
        ctk.CTkLabel(details_frame, text="Category:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=item['category'] or "N/A", font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Unit
        ctk.CTkLabel(details_frame, text="Unit:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=item['unit_name'] or "N/A", font=ctk.CTkFont(size=12)).grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Purchase Price
        ctk.CTkLabel(details_frame, text="Purchase:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=f"₹{item['purchase_price']:.2f}", font=ctk.CTkFont(size=12)).grid(row=2, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Selling Price
        ctk.CTkLabel(details_frame, text="Selling:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=f"₹{item['selling_price']:.2f}", font=ctk.CTkFont(size=12)).grid(row=3, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # GST Rate
        gst_display = f"{item['gst_rate']:.2f}%" if item['gst_rate'] is not None else "N/A"
        ctk.CTkLabel(details_frame, text="GST:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=gst_display, font=ctk.CTkFont(size=12)).grid(row=4, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Stock Level
        ctk.CTkLabel(details_frame, text="Min Stock:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, sticky="w", pady=2)
        ctk.CTkLabel(details_frame, text=str(item['minimum_stock_level']), font=ctk.CTkFont(size=12)).grid(row=5, column=1, sticky="w", padx=(5, 0), pady=2)
        
        # Action buttons
        button_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(button_frame, text="Edit", width=60, height=25, font=ctk.CTkFont(size=10),
                     command=lambda i=item: self.edit_item(i)).pack(side="left", padx=2)
        ctk.CTkButton(button_frame, text="Delete", width=60, height=25, font=ctk.CTkFont(size=10),
                     command=lambda i=item: self.delete_item(i), fg_color="red", hover_color="darkred").pack(side="left", padx=2)
        
        return card_frame
        
    def edit_item(self, item):
        """Edit an item by switching to table view and populating form"""
        self.show_table_view()
        
        # Populate form with item data
        self.clear_form()
        self.name_entry.insert(0, item['name'])
        self.purchase_price_entry.insert(0, f"{item['purchase_price']:.2f}")
        self.selling_price_entry.insert(0, f"{item['selling_price']:.2f}")
        self.warranty_entry.insert(0, str(item['default_warranty_months']))
        self.min_stock_entry.insert(0, str(item['minimum_stock_level']))
        self.category_entry.insert(0, item['category'] or "")

        if item['unit_id'] in self.unit_id_map: 
            self.unit_var.set(self.unit_id_map[item['unit_id']])
        if item['hsn_code_id'] in self.hsn_id_map: 
            self.hsn_var.set(self.hsn_id_map[item['hsn_code_id']])
        if item['gst_slab_id'] in self.gst_slab_id_map: 
            self.gst_var.set(self.gst_slab_id_map[item['gst_slab_id']])

        self.update_button.configure(state="normal")
        self.add_button.configure(state="disabled")
        
        # Store the item ID for updating
        self.editing_item_id = item['id']
        
    def delete_item(self, item):
        """Delete an item"""
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete item '{item['name']}'?")
        if result:
            # In a real implementation, you would delete from database
            # For now, we'll just reload the items
            if hasattr(self, 'current_view') and self.current_view == "card":
                self.load_items_cards()
            else:
                self.load_items_table()
            messagebox.showinfo("Success", "Item deleted successfully.")
            
    def load_items_table(self):
        """Load items into the table view"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        items = db_manager.get_all_items()
        for item in items:
            gst_display = f"{item['gst_rate']:.2f}" if item['gst_rate'] is not None else "N/A"
            tree_values = (item['id'], item['name'], item['category'], item['unit_name'], item['hsn_code'], gst_display, f"{item['purchase_price']:.2f}", f"{item['selling_price']:.2f}", item['default_warranty_months'], item['minimum_stock_level'])
            self.tree.insert("", "end", values=tree_values)

    def load_data(self):
        """Load all necessary data from DB and populate the form and treeview."""
        # Load units
        all_units = db_manager.get_all_units()
        self.unit_map = {unit['name']: unit['id'] for unit in all_units}
        self.unit_id_map = {unit['id']: unit['name'] for unit in all_units}
        self.unit_option_menu.configure(values=list(self.unit_map.keys()))

        # Load HSN codes
        self.hsn_data = db_manager.get_all_hsn_codes_with_details()
        self.hsn_map = {f"{h['hsn_code']} - {h['description']}": h['id'] for h in self.hsn_data}
        self.hsn_id_map = {h['id']: f"{h['hsn_code']} - {h['description']}" for h in self.hsn_data}
        self.hsn_option_menu.configure(values=[""] + list(self.hsn_map.keys()))

        # Load GST slabs
        all_slabs = db_manager.get_all_gst_slabs()
        self.gst_slab_map = {f"{s['rate']}%": s['id'] for s in all_slabs}
        self.gst_slab_id_map = {s['id']: f"{s['rate']}%" for s in all_slabs}
        self.gst_option_menu.configure(values=list(self.gst_slab_map.keys()))

        # Load items into treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        items = db_manager.get_all_items()
        for item in items:
            gst_display = f"{item['gst_rate']:.2f}" if item['gst_rate'] is not None else "N/A"
            tree_values = (item['id'], item['name'], item['category'], item['unit_name'], item['hsn_code'], gst_display, f"{item['purchase_price']:.2f}", f"{item['selling_price']:.2f}", item['default_warranty_months'], item['minimum_stock_level'])
            self.tree.insert("", "end", values=tree_values)
        self.clear_form()
        
        # Load appropriate view
        if hasattr(self, 'current_view'):
            if self.current_view == "card":
                self.load_items_cards()
            else:
                self.load_items_table()
        else:
            # Default to card view
            self.load_items_cards()

    def on_hsn_select_in_form(self, selected_hsn_str):
        """When an HSN is selected in the form, auto-select the default GST slab."""
        hsn_id = self.hsn_map.get(selected_hsn_str)
        if not hsn_id: return

        hsn_info = next((h for h in self.hsn_data if h['id'] == hsn_id), None)
        if hsn_info and hsn_info['gst_slab_id'] in self.gst_slab_id_map:
            self.gst_var.set(self.gst_slab_id_map[hsn_info['gst_slab_id']])
        else:
            self.gst_var.set("") # Clear if no default slab

    def get_form_data(self):
        try:
            name = self.name_entry.get().strip()
            purchase = float(self.purchase_price_entry.get() or 0)
            selling = float(self.selling_price_entry.get() or 0)
            warranty = int(self.warranty_entry.get() or 0)
            min_stock = int(self.min_stock_entry.get() or 0)
            category = self.category_entry.get().strip()

            unit_id = self.unit_map.get(self.unit_var.get())
            hsn_id = self.hsn_map.get(self.hsn_var.get())
            gst_id = self.gst_slab_map.get(self.gst_var.get())

            if not all([name, unit_id, hsn_id, gst_id]):
                messagebox.showerror("Validation Error", "Name, Unit, HSN Code, and GST Slab are required.", parent=self)
                return None

            return (name, purchase, selling, warranty, min_stock, category, unit_id, hsn_id, gst_id, False)
        except (ValueError, TypeError):
            messagebox.showerror("Validation Error", "Please enter valid numbers for prices, warranty, and stock level.", parent=self)
            return None

    def add_item(self):
        data = self.get_form_data()
        if data:
            if db_manager.add_item(*data):
                messagebox.showinfo("Success", "Item added successfully.", parent=self)
                self.load_data()
            else:
                messagebox.showerror("Database Error", f"Could not add item. '{data[0]}' may already exist.", parent=self)

    def update_item(self):
        # Check if we have an item ID from card editing
        if hasattr(self, 'editing_item_id'):
            item_id = self.editing_item_id
        else:
            selected = self.tree.focus()
            if not selected: return
            item_id = self.tree.item(selected, "values")[0]

        data = self.get_form_data()
        if data:
            if db_manager.update_item(item_id, *data):
                messagebox.showinfo("Success", "Item updated successfully.", parent=self)
                self.load_data()
                if hasattr(self, 'editing_item_id'):
                    delattr(self, 'editing_item_id')
            else:
                messagebox.showerror("Database Error", "Could not update item.", parent=self)

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.purchase_price_entry.delete(0, "end")
        self.selling_price_entry.delete(0, "end")
        self.warranty_entry.delete(0, "end")
        self.min_stock_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.unit_var.set("")
        self.hsn_var.set("")
        self.gst_var.set("")
        if self.tree.selection(): self.tree.selection_remove(self.tree.selection()[0])
        self.update_button.configure(state="disabled")
        self.add_button.configure(state="normal")
        self.name_entry.focus()

    def on_tree_select(self, event):
        selected_item_id = self.tree.focus()
        if not selected_item_id: return

        item_data = db_manager.get_all_items() # Inefficient, but simple. Better to get one item by ID.
        selected_item = next((item for item in item_data if item['id'] == int(self.tree.item(selected_item_id, "values")[0])), None)

        if selected_item:
            self.clear_form()
            self.name_entry.insert(0, selected_item['name'])
            self.purchase_price_entry.insert(0, f"{selected_item['purchase_price']:.2f}")
            self.selling_price_entry.insert(0, f"{selected_item['selling_price']:.2f}")
            self.warranty_entry.insert(0, selected_item['default_warranty_months'])
            self.min_stock_entry.insert(0, selected_item['minimum_stock_level'])
            self.category_entry.insert(0, selected_item['category'])

            if selected_item['unit_id'] in self.unit_id_map: self.unit_var.set(self.unit_id_map[selected_item['unit_id']])
            if selected_item['hsn_code_id'] in self.hsn_id_map: self.hsn_var.set(self.hsn_id_map[selected_item['hsn_code_id']])
            if selected_item['gst_slab_id'] in self.gst_slab_id_map: self.gst_var.set(self.gst_slab_id_map[selected_item['gst_slab_id']])

            self.update_button.configure(state="normal")
            self.add_button.configure(state="disabled")
