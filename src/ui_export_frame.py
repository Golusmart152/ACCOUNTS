import customtkinter as ctk
from tkinter import filedialog, messagebox
import db_manager
import csv_generator
import pdf_generator
import datetime

class ExportFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Export Data", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=10)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=10, pady=10, fill="x", expand=False)

        ctk.CTkLabel(main_frame, text="Data to Export:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.data_type_var = ctk.StringVar(value="Items")
        self.data_type_menu = ctk.CTkOptionMenu(main_frame, variable=self.data_type_var,
                                                values=["Items", "Customers", "Suppliers", "Sales Invoices", "Purchase Invoices"])
        self.data_type_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(main_frame, text="Export Format:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.format_var = ctk.StringVar(value="CSV")
        self.format_menu = ctk.CTkOptionMenu(main_frame, variable=self.format_var, values=["CSV", "PDF"])
        self.format_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.export_button = ctk.CTkButton(main_frame, text="Export Data", command=self.export_data)
        self.export_button.grid(row=2, column=1, padx=10, pady=20, sticky="e")

    def export_data(self):
        data_type = self.data_type_var.get()
        export_format = self.format_var.get().lower()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
        suggested_filename = f"export_{data_type.lower().replace(' ', '_')}_{timestamp}.{export_format}"

        file_path = filedialog.asksaveasfilename(
            title=f"Export {data_type} to {export_format.upper()}",
            initialfile=suggested_filename,
            defaultextension=f".{export_format}",
            filetypes=[(f"{export_format.upper()} files", f"*.{export_format}"), ("All files", "*.*")]
        )

        if not file_path:
            return

        fetch_functions = {
            "Items": db_manager.get_items_for_export,
            "Customers": db_manager.get_customers_for_export,
            "Suppliers": db_manager.get_suppliers_for_export,
            "Sales Invoices": db_manager.get_sales_invoices_for_export,
            "Purchase Invoices": db_manager.get_purchase_invoices_for_export,
        }

        fetch_function = fetch_functions.get(data_type)
        if not fetch_function:
            messagebox.showerror("Error", f"No export function defined for '{data_type}'.", parent=self)
            return

        try:
            data_to_export = fetch_function()
            if not data_to_export:
                messagebox.showinfo("No Data", f"There is no data for '{data_type}' to export.", parent=self)
                return

            if export_format == "csv":
                success, error_msg = csv_generator.export_to_csv(data_to_export, file_path)
                if success:
                    messagebox.showinfo("Success", f"{data_type} exported to CSV successfully.", parent=self)
                else:
                    messagebox.showerror("Export Error", f"Failed to export to CSV: {error_msg}", parent=self)

            elif export_format == "pdf":
                title = f"{data_type} Report - {timestamp}"
                success, error_msg = pdf_generator.export_to_pdf(data_to_export, file_path, title)
                if success:
                    messagebox.showinfo("Success", f"{data_type} exported to PDF successfully.", parent=self)
                else:
                    messagebox.showerror("Export Error", f"Failed to export to PDF: {error_msg}", parent=self)

            else:
                messagebox.showerror("Error", f"Unsupported format: {export_format}", parent=self)

        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during export: {e}", parent=self)


    def load_data(self):
        # This frame doesn't need to load any data from the DB to be displayed
        pass
