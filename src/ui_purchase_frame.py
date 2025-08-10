import customtkinter as ctk
from tkinter import ttk, messagebox
from . import db_manager
from .ui_serial_dialog import SerialEntryDialog
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PurchaseFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.invoice_items = []
        self.current_item_units = []
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Create Purchase Invoice", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1); header_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(header_frame, text="Supplier:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.supplier_combo = ctk.CTkComboBox(header_frame, values=[], command=self.supplier_changed)
        self.supplier_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Invoice #:").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        self.invoice_no_entry = ctk.CTkEntry(header_frame)
        self.invoice_no_entry.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Invoice Date:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.invoice_date_entry = ctk.CTkEntry(header_frame, placeholder_text="YYYY-MM-DD")
        self.invoice_date_entry.insert(0, datetime.date.today().isoformat())
        self.invoice_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(header_frame, text="Notes:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.notes_entry = ctk.CTkEntry(header_frame)
        self.notes_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        items_frame = ctk.CTkFrame(self)
        items_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        items_frame.grid_columnconfigure(0, weight=1); items_frame.grid_rowconfigure(1, weight=1)

        self.create_item_entry_form(items_frame)

        columns = ("item_name", "qty", "unit", "price", "gst", "total", "serials")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        for col in columns: self.items_tree.heading(col, text=col.replace("_", " ").title())
        self.items_tree.column("serials", width=200)
        self.items_tree.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.total_label = ctk.CTkLabel(footer_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.total_label.pack(side="right", padx=10)
        self.save_button = ctk.CTkButton(footer_frame, text="Save Purchase Invoice", command=self.save_invoice)
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

        self.add_item_button = ctk.CTkButton(entry_form, text="Add to Bill", width=100, command=self.add_item_to_invoice)
        self.add_item_button.pack(side="left", padx=10)

    def load_data(self):
        self.suppliers = db_manager.get_all_suppliers()
        self.items = db_manager.get_all_items()
        self.supplier_combo.configure(values=[s['name'] for s in self.suppliers])

        # Filter for non-assembled items for the dropdown
        self.purchasable_items = [i for i in self.items if not i['is_assembled_item']]
        self.item_combo.configure(values=[i['name'] for i in self.purchasable_items])

        self.invoice_items.clear()
        self.refresh_items_tree()
        self.update_total()
        self.invoice_no_entry.delete(0, "end")
        self.invoice_date_entry.delete(0, "end"); self.invoice_date_entry.insert(0, datetime.date.today().isoformat())
        self.notes_entry.delete(0, "end")

        if self.suppliers: self.supplier_combo.set(self.suppliers[0]['name'])
        if self.purchasable_items: self.item_combo.set(self.purchasable_items[0]['name']); self.item_changed()

    def supplier_changed(self, choice): pass

    def item_changed(self, choice=None):
        item_name = self.item_combo.get()
        item = next((i for i in self.purchasable_items if i['name'] == item_name), None)
        if item:
            self.price_entry.delete(0, "end")
            if item['purchase_price']: self.price_entry.insert(0, str(item['purchase_price']))

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
        selected_item_name = self.item_combo.get()
        qty_str = self.qty_entry.get(); price_str = self.price_entry.get()
        selected_unit_name = self.unit_var.get()

        if not all([selected_item_name, qty_str, price_str, selected_unit_name]):
            return messagebox.showerror("Error", "Please fill all item fields, including unit.", parent=self)
        try:
            qty = float(qty_str); price = float(price_str)
        except ValueError:
            return messagebox.showerror("Error", "Quantity and Price must be numbers.", parent=self)

        item = next((i for i in self.purchasable_items if i['name'] == selected_item_name), None)
        if not item: return messagebox.showerror("Error", "Item not found.", parent=self)

        # Find conversion factor
        unit_info = next((u for u in self.current_item_units if u['name'] == selected_unit_name), None)
        if not unit_info: return messagebox.showerror("Error", "Invalid unit selected for this item.", parent=self)

        conversion_factor = unit_info['factor']
        base_quantity = qty * conversion_factor

        serials = []
        if item['is_serialized']:
            if base_quantity != int(base_quantity):
                return messagebox.showerror("Error", "Quantity for serialized items must result in a whole number of base units.", parent=self)
            dialog = SerialEntryDialog(self, int(base_quantity))
            serials = dialog.get_serials()
            if len(serials) != int(base_quantity): return # User cancelled or did not enter all serials

        gst_amount = (qty * price) * (item['gst_rate'] / 100)
        self.invoice_items.append({
            "item_id": item['id'], "item_name": selected_item_name,
            "quantity": base_quantity, # Store quantity in base unit
            "display_quantity": qty, # For display
            "display_unit": selected_unit_name, # For display
            "purchase_price": price / conversion_factor, # Store price per base unit
            "display_price": price, # For display
            "gst_rate": item['gst_rate'], "gst_amount": gst_amount,
            "serial_numbers": serials, "godown_id": 1 # Hardcoded godown for now
        })
        self.refresh_items_tree(); self.update_total()
        self.qty_entry.delete(0, 'end')

    def refresh_items_tree(self):
        for i in self.items_tree.get_children(): self.items_tree.delete(i)
        for item in self.invoice_items:
            serials_str = ", ".join(item['serial_numbers']) if item['serial_numbers'] else "N/A"
            total = (item['display_quantity'] * item['display_price']) + item['gst_amount']
            self.items_tree.insert("", "end", values=(item['item_name'], item['display_quantity'], item['display_unit'], f"{item['display_price']:.2f}", f"{item['gst_rate']}%", f"{total:.2f}", serials_str))

    def update_total(self):
        total = sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items)
        self.total_label.configure(text=f"Total: ₹{total:,.2f}")

    def save_invoice(self):
        supplier_name = self.supplier_combo.get()
        invoice_no = self.invoice_no_entry.get().strip()
        invoice_date = self.invoice_date_entry.get().strip()
        if not all([supplier_name, invoice_no, invoice_date]): return messagebox.showerror("Error", "Supplier, Invoice #, and Date are required.", parent=self)
        if not self.invoice_items: return messagebox.showerror("Error", "Please add at least one item to the invoice.", parent=self)

        supplier = next((s for s in self.suppliers if s['name'] == supplier_name), None)
        if not supplier: return messagebox.showerror("Error", "Invalid supplier selected.", parent=self)

        total_amount = sum((i['display_quantity'] * i['display_price']) + i['gst_amount'] for i in self.invoice_items)
        total_gst = sum(i['gst_amount'] for i in self.invoice_items)

        invoice_data = {
            "supplier_id": supplier['id'], "invoice_number": invoice_no, "invoice_date": invoice_date,
            "total_amount": total_amount, "gst_amount": total_gst,
            "notes": self.notes_entry.get().strip()
        }

        # The backend expects quantity and price per base unit.
        invoice_id = db_manager.create_purchase_invoice_transaction(invoice_data, self.invoice_items)

        if invoice_id:
            messagebox.showinfo("Success", f"Purchase Invoice #{invoice_id} saved successfully.", parent=self)
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to save invoice. Check logs for details.", parent=self)
