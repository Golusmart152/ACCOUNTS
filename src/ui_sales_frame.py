import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager
from .ui_serial_selector_dialog import SerialSelectorDialog
import datetime

class SalesFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.invoice_items = []
        self.current_item_units = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(self, text="Create Sales Invoice", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1); header_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(header_frame, text="Customer:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.customer_combo = ctk.CTkComboBox(header_frame, values=[])
        self.customer_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Invoice #:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.invoice_no_label = ctk.CTkLabel(header_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.invoice_no_label.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(header_frame, text="Invoice Date:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.invoice_date_entry = ctk.CTkEntry(header_frame, placeholder_text="YYYY-MM-DD")
        self.invoice_date_entry.insert(0, datetime.date.today().isoformat())
        self.invoice_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        items_frame = ctk.CTkFrame(self)
        items_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        items_frame.grid_columnconfigure(0, weight=1); items_frame.grid_rowconfigure(1, weight=1)
        self.create_item_entry_form(items_frame)

        columns = ("item_name", "qty", "unit", "price", "gst", "total", "serials")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        for col in columns: self.items_tree.heading(col, text=col.replace("_", " ").title())
        self.items_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.total_label = ctk.CTkLabel(footer_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(side="right", padx=10)
        self.save_button = ctk.CTkButton(footer_frame, text="Save Sales Invoice", command=self.save_invoice)
        self.save_button.pack(side="right", padx=10)

    def create_item_entry_form(self, parent):
        entry_form = ctk.CTkFrame(parent)
        entry_form.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(entry_form, text="Item:").pack(side="left", padx=5)
        self.item_combo = ctk.CTkComboBox(entry_form, values=[], command=self.item_changed)
        self.item_combo.pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkLabel(entry_form, text="Qty:").pack(side="left", padx=5)
        self.qty_entry = ctk.CTkEntry(entry_form, width=80)
        self.qty_entry.pack(side="left", padx=5)

        ctk.CTkLabel(entry_form, text="Unit:").pack(side="left", padx=5)
        self.unit_var = ctk.StringVar()
        self.unit_option_menu = ctk.CTkOptionMenu(entry_form, variable=self.unit_var, values=[], width=100)
        self.unit_option_menu.pack(side="left", padx=5)

        ctk.CTkLabel(entry_form, text="Price/Unit:").pack(side="left", padx=5)
        self.price_entry = ctk.CTkEntry(entry_form, width=100)
        self.price_entry.pack(side="left", padx=5)
        self.add_item_button = ctk.CTkButton(entry_form, text="Add Item", width=100, command=self.add_item_to_invoice)
        self.add_item_button.pack(side="left", padx=10)

    def item_changed(self, choice=None):
        item_name = self.item_combo.get()
        item = next((i for i in self.items if i['name'] == item_name), None)
        if item:
            self.price_entry.delete(0, "end")
            if item['selling_price']: self.price_entry.insert(0, str(item['selling_price']))

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
        item_name=self.item_combo.get(); qty_str=self.qty_entry.get(); price_str=self.price_entry.get(); unit_name=self.unit_var.get()
        if not all([item_name, qty_str, price_str, unit_name]): return messagebox.showerror("Error", "Please fill all item fields.", parent=self)
        try: qty=float(qty_str); price=float(price_str)
        except ValueError: return messagebox.showerror("Error", "Qty and Price must be numbers.", parent=self)

        item = next((i for i in self.items if i['name'] == item_name), None)
        if not item: return messagebox.showerror("Error", "Item not found.", parent=self)

        unit_info = next((u for u in self.current_item_units if u['name'] == unit_name), None)
        if not unit_info: return messagebox.showerror("Error", "Invalid unit selected for this item.", parent=self)

        conversion_factor = unit_info['factor']
        base_quantity = qty * conversion_factor

        serial_ids, serial_numbers = [], []
        if item['is_serialized']:
            if base_quantity != int(base_quantity):
                return messagebox.showerror("Error", "Quantity for serialized items must result in a whole number of base units.", parent=self)
            available = db_manager.get_available_serial_numbers_for_item(item['id'])
            if len(available) < base_quantity: return messagebox.showerror("Stock Error", f"Not enough stock for {item_name}. Required: {int(base_quantity)}, Available: {len(available)}", parent=self)
            dialog = SerialSelectorDialog(self, item_name, available, int(base_quantity))
            serial_ids = dialog.get_selected_ids()
            if len(serial_ids) != int(base_quantity): return # Cancelled or not enough selected
            serial_numbers = [dict(s)['serial_number'] for s in available if str(dict(s)['id']) in serial_ids]

        gst = (qty * price) * (item['gst_rate'] / 100)
        self.invoice_items.append({
            "item_id": item['id'], "item_name": item_name, "quantity": base_quantity, "selling_price": price / conversion_factor,
            "display_quantity": qty, "display_unit": unit_name, "display_price": price,
            "gst_rate": item['gst_rate'], "gst_amount": gst, "serial_ids": serial_ids, "serial_numbers": serial_numbers
        })
        self.refresh_items_tree(); self.update_total()
        self.qty_entry.delete(0, 'end')

    def refresh_items_tree(self):
        for i in self.items_tree.get_children(): self.items_tree.delete(i)
        for item in self.invoice_items:
            total = (item['display_quantity'] * item['display_price']) + item['gst_amount']
            self.items_tree.insert("", "end", values=(item['item_name'], item['display_quantity'], item['display_unit'], f"{item['display_price']:.2f}", f"{item['gst_rate']}%", f"{total:.2f}", ", ".join(item['serial_numbers'])))

    def update_total(self):
        total = sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items)
        self.total_label.configure(text=f"Total: ₹{total:,.2f}")

    def save_invoice(self):
        cust_name=self.customer_combo.get(); inv_date=self.invoice_date_entry.get().strip()
        if not all([cust_name, inv_date]): return messagebox.showerror("Error", "Customer and Invoice Date are required.", parent=self)
        if not self.invoice_items: return messagebox.showerror("Error", "Please add items to the invoice.", parent=self)
        cust = next((c for c in self.customers if c['name'] == cust_name), None)
        if not cust: return messagebox.showerror("Error", "Invalid customer.", parent=self)

        invoice_data = {
            "customer_id": cust['id'], "invoice_number": self.invoice_no_label.cget("text"), "invoice_date": inv_date,
            "total_amount": sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items),
            "gst_amount": sum(i['gst_amount'] for i in self.invoice_items), "notes": ""
        }

        inv_id = db_manager.create_sale_invoice_transaction(invoice_data, self.invoice_items)
        if inv_id:
            messagebox.showinfo("Success", f"Sales Invoice {self.invoice_no_label.cget('text')} saved successfully.", parent=self)
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to save invoice. Check logs for details.", parent=self)

    def load_data(self):
        self.customers = db_manager.get_all_customers()
        self.items = db_manager.get_all_items()
        self.customer_combo.configure(values=[c['name'] for c in self.customers])
        self.item_combo.configure(values=[i['name'] for i in self.items])
        self.invoice_no_label.configure(text=db_manager.get_next_invoice_number())
        self.invoice_items.clear()
        self.refresh_items_tree()
        self.update_total()
        self.customer_combo.set(self.customers[0]['name'] if self.customers else "")
        self.item_combo.set(self.items[0]['name'] if self.items else "")
        if self.items: self.item_changed()
