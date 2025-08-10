import customtkinter as ctk
from tkinter import ttk
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class SalesInvoiceDetailDialog(ctk.CTkToplevel):
    def __init__(self, master, invoice_data, item_data):
        super().__init__(master)

        self.title(f"Details for Invoice #{invoice_data['invoice_number']}")
        self.geometry("800x600")
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(3, weight=1)

        # Display Invoice Header Info
        ctk.CTkLabel(header_frame, text="Customer:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(header_frame, text=invoice_data['customer_name']).grid(row=0, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(header_frame, text="Invoice #:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(header_frame, text=invoice_data['invoice_number']).grid(row=0, column=3, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(header_frame, text="Date:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(header_frame, text=invoice_data['invoice_date']).grid(row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(header_frame, text="Status:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, padx=10, pady=2, sticky="w")
        ctk.CTkLabel(header_frame, text=invoice_data['status']).grid(row=1, column=3, padx=10, pady=2, sticky="w")

        # Items Treeview
        items_frame = ctk.CTkFrame(self)
        items_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_rowconfigure(0, weight=1)

        columns = ("name", "hsn", "qty", "price", "gst", "total")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")
        for col in columns: self.items_tree.heading(col, text=col.title())
        self.items_tree.grid(row=0, column=0, sticky="nsew")

        for item in item_data:
            total = (item['quantity'] * item['selling_price']) * (1 + item['gst_rate']/100)
            self.items_tree.insert("", "end", values=(
                item['item_name'], item['hsn_code'], item['quantity'],
                f"{item['selling_price']:.2f}", f"{item['gst_rate']:.2f}%", f"{total:.2f}"
            ))

        # Totals Footer
        footer_frame = ctk.CTkFrame(self)
        footer_frame.grid(row=2, column=0, padx=10, pady=10, sticky="e")

        total_text = f"Total: ₹{invoice_data['total_amount']:,.2f} | GST: ₹{invoice_data['gst_amount']:,.2f}"
        ctk.CTkLabel(footer_frame, text=total_text, font=ctk.CTkFont(size=14, weight="bold")).pack()

        close_button = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_button.grid(row=3, column=0, padx=10, pady=10)
