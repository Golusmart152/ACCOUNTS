import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import db_manager
import csv_generator
import csv_validator
import os

class ImportFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.validated_data = []

        self.create_controls_frame()
        self.create_preview_frame()

    def create_controls_frame(self):
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls_frame, text="Import Data", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(controls_frame, text="Data to Import:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.data_type_var = ctk.StringVar(value="Items")
        self.data_type_menu = ctk.CTkOptionMenu(controls_frame, variable=self.data_type_var,
                                                values=["Items", "Customers", "Suppliers", "Purchase Invoices"])
        self.data_type_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(controls_frame, text="Step 1:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.download_button = ctk.CTkButton(controls_frame, text="Download Sample Template", command=self.download_template)
        self.download_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(controls_frame, text="Step 2:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.upload_button = ctk.CTkButton(controls_frame, text="Upload and Validate CSV", command=self.upload_and_validate)
        self.upload_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.upload_path_label = ctk.CTkLabel(controls_frame, text="No file selected.", text_color="gray", wraplength=400)
        self.upload_path_label.grid(row=3, column=2, padx=10, pady=10, sticky="w")

    def create_preview_frame(self):
        preview_frame = ctk.CTkFrame(self)
        preview_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(preview_frame, text="Step 3: Preview and Commit", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.preview_tree = ttk.Treeview(preview_frame)
        self.preview_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        button_frame = ctk.CTkFrame(preview_frame)
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.summary_label = ctk.CTkLabel(button_frame, text="Summary: 0 valid, 0 invalid.")
        self.summary_label.pack(side="left", padx=10)
        self.commit_button = ctk.CTkButton(button_frame, text="Commit Valid Data", state="disabled", command=self.commit_data)
        self.commit_button.pack(side="left", padx=10)

    def download_template(self):
        data_type = self.data_type_var.get()

        template_functions = {
            "Items": csv_generator.generate_items_template,
            "Customers": csv_generator.generate_customers_template,
            "Suppliers": csv_generator.generate_suppliers_template,
            "Purchase Invoices": csv_generator.generate_purchases_template,
        }
        template_func = template_functions.get(data_type)
        if not template_func:
            return messagebox.showwarning("Not Implemented", f"Template generation for '{data_type}' is not yet implemented.", parent=self)

        file_path = filedialog.asksaveasfilename(title=f"Save {data_type} Import Template", initialfile=f"{data_type.lower().replace(' ', '_')}_import_template.csv", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path: return

        success, error_msg = template_func(file_path)
        if success:
            messagebox.showinfo("Success", f"Template saved successfully to:\n{file_path}", parent=self)
        else:
            messagebox.showerror("Error", f"Failed to save template: {error_msg}", parent=self)

    def upload_and_validate(self):
        file_path = filedialog.askopenfilename(title="Select CSV File to Import", filetypes=[("CSV files", "*.csv")])
        if not file_path: return

        self.upload_path_label.configure(text=os.path.basename(file_path))
        data_type = self.data_type_var.get()

        validation_functions = {
            "Items": csv_validator.validate_items_csv,
            "Customers": csv_validator.validate_customers_csv,
            "Suppliers": csv_validator.validate_suppliers_csv,
            "Purchase Invoices": csv_validator.validate_purchases_csv,
        }
        validation_func = validation_functions.get(data_type)
        if not validation_func:
            return messagebox.showwarning("Not Implemented", f"Import for '{data_type}' is not yet implemented.", parent=self)

        self.validated_data, error_msg = validation_func(file_path)
        if error_msg:
            return messagebox.showerror("Validation Error", f"Failed to read or validate file: {error_msg}", parent=self)

        self.populate_preview_tree(data_type)

    def populate_preview_tree(self, data_type):
        for i in self.preview_tree.get_children(): self.preview_tree.delete(i)

        if not self.validated_data: return

        if data_type == "Purchase Invoices":
            self.populate_purchase_invoice_preview()
        else:
            self.populate_flat_preview()

    def populate_flat_preview(self):
        headers = list(self.validated_data[0]['data'].keys())
        all_columns = ["is_valid", "errors"] + headers
        self.preview_tree["columns"] = all_columns
        self.preview_tree.heading("#0", text="", anchor="w")
        self.preview_tree.column("#0", width=0, stretch=False)
        for col in all_columns:
            self.preview_tree.heading(col, text=col.title().replace("_", " "))
            self.preview_tree.column(col, width=100, anchor="w")

        self.preview_tree.tag_configure('valid', background='lightgreen')
        self.preview_tree.tag_configure('invalid', background='lightcoral')

        valid_count, invalid_count = 0, 0
        for row_data in self.validated_data:
            tag = 'valid' if row_data['is_valid'] else 'invalid'
            if row_data['is_valid']: valid_count += 1
            else: invalid_count += 1

            values = [row_data['is_valid'], row_data['errors']] + [row_data['data'].get(h, '') for h in headers]
            self.preview_tree.insert("", "end", values=values, tags=(tag,))

        self.summary_label.configure(text=f"Summary: {valid_count} valid, {invalid_count} invalid.")
        self.commit_button.configure(state="normal" if valid_count > 0 else "disabled")

    def populate_purchase_invoice_preview(self):
        all_columns = ["is_valid", "invoice_number", "supplier_name", "invoice_date", "errors", "item_name", "item_errors"]
        self.preview_tree["columns"] = all_columns
        for col in all_columns: self.preview_tree.heading(col, text=col.title().replace("_", " "))

        self.preview_tree.tag_configure('valid_header', background='lightblue')
        self.preview_tree.tag_configure('invalid_header', background='lightcoral')
        self.preview_tree.tag_configure('valid_item', background='lightgreen')
        self.preview_tree.tag_configure('invalid_item', background='#FFDAB9') # Peach

        valid_count, invalid_count = 0, 0
        for inv in self.validated_data:
            tag = 'valid_header' if inv['is_valid'] else 'invalid_header'
            if inv['is_valid']: valid_count += 1
            else: invalid_count += 1

            header = inv['data']['header']
            header_values = [inv['is_valid'], header.get('invoice_number'), header.get('supplier_name'), header.get('invoice_date'), inv['errors'], "", ""]
            parent = self.preview_tree.insert("", "end", values=header_values, tags=(tag,), text="INV")

            for item_line in inv['data']['items']:
                item_tag = 'valid_item' if not item_line['errors'] else 'invalid_item'
                item_values = ["", "", "", "", "", item_line['data'].get('item_name'), item_line['errors']]
                self.preview_tree.insert(parent, "end", values=item_values, tags=(item_tag,))

        self.summary_label.configure(text=f"Summary: {valid_count} valid invoices, {invalid_count} invalid.")
        self.commit_button.configure(state="normal" if valid_count > 0 else "disabled")


    def commit_data(self):
        data_type = self.data_type_var.get()
        valid_rows = [row for row in self.validated_data if row['is_valid']]
        if not valid_rows:
            return messagebox.showwarning("No Data", "There are no valid rows to import.", parent=self)

        import_functions = {
            "Items": db_manager.import_items_from_data,
            "Customers": db_manager.import_customers_from_data,
            "Suppliers": db_manager.import_suppliers_from_data,
            "Purchase Invoices": db_manager.import_purchases_from_data,
        }
        import_func = import_functions.get(data_type)
        if not import_func:
            return messagebox.showwarning("Not Implemented", f"Commit logic for '{data_type}' is not yet implemented.", parent=self)

        confirm = messagebox.askyesno("Confirm Import", f"Are you sure you want to import {len(valid_rows)} {data_type} record(s)?", parent=self)
        if not confirm: return

        # The function signature for purchases is different
        if data_type == "Purchase Invoices":
            success, imported_count, error_msg = import_func(valid_rows)
            if success:
                messagebox.showinfo("Success", f"Import complete. {imported_count} purchase invoices were created.", parent=self)
            else:
                messagebox.showerror("Database Error", f"An error occurred during import: {error_msg}", parent=self)
        else:
            success, inserted, updated, error_msg = import_func(valid_rows)
            if success:
                messagebox.showinfo("Success", f"Import complete for {data_type}.\n\nNew records inserted: {inserted}\nExisting records updated: {updated}", parent=self)
            else:
                messagebox.showerror("Database Error", f"An error occurred during import: {error_msg}", parent=self)

        self.load_data()


    def load_data(self):
        for i in self.preview_tree.get_children(): self.preview_tree.delete(i)
        self.validated_data = []
        self.commit_button.configure(state="disabled")
        self.summary_label.configure(text="Summary: 0 valid, 0 invalid.")
        self.upload_path_label.configure(text="No file selected.")
