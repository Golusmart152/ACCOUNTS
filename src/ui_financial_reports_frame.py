import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager
import pdf_generator

class FinancialReportsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Financial Reports", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w")

        # --- Controls ---
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        ctk.CTkLabel(controls_frame, text="Start Date:").pack(side="left", padx=5)
        self.start_date_entry = ctk.CTkEntry(controls_frame, placeholder_text="YYYY-MM-DD")
        self.start_date_entry.pack(side="left", padx=5)

        ctk.CTkLabel(controls_frame, text="End Date:").pack(side="left", padx=5)
        self.end_date_entry = ctk.CTkEntry(controls_frame, placeholder_text="YYYY-MM-DD")
        self.end_date_entry.pack(side="left", padx=5)

        ctk.CTkButton(controls_frame, text="Generate P&L", command=self.generate_pl).pack(side="left", padx=10)
        ctk.CTkButton(controls_frame, text="Generate Balance Sheet", command=self.generate_bs).pack(side="left", padx=10)
        ctk.CTkButton(controls_frame, text="Generate GSTR-1", command=self.generate_gstr1).pack(side="left", padx=10)
        ctk.CTkButton(controls_frame, text="Generate GSTR-3B", command=self.generate_gstr3b).pack(side="left", padx=10)


        # --- Report Display ---
        self.report_textbox = ctk.CTkTextbox(self, font=("Courier", 12))
        self.report_textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def load_data(self):
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, first_day_of_month.isoformat())
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, today.isoformat())
        self.report_textbox.delete("1.0", "end")

    def generate_pl(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        data = db_manager.get_profit_and_loss_data(start_date, end_date)

        report = f"Profit & Loss Statement\nFrom {start_date} to {end_date}\n"
        report += "="*40 + "\n\n"

        revenues = {r['name']: abs(r['total_credits'] - r['total_debits']) for r in data if r['type'] == 'Revenue'}
        expenses = {r['name']: abs(r['total_debits'] - r['total_credits']) for r in data if r['type'] == 'Expense'}

        total_revenue = sum(revenues.values())
        total_expense = sum(expenses.values())
        net_profit = total_revenue - total_expense

        report += "Revenues:\n"
        for name, amount in revenues.items():
            report += f"  {name:<25} {amount:10.2f}\n"
        report += f"  {'-'*25} ----------\n"
        report += f"  {'Total Revenue':<25} {total_revenue:10.2f}\n\n"

        report += "Expenses:\n"
        for name, amount in expenses.items():
            report += f"  {name:<25} {amount:10.2f}\n"
        report += f"  {'-'*25} ----------\n"
        report += f"  {'Total Expenses':<25} {total_expense:10.2f}\n\n"

        report += "="*40 + "\n"
        report += f"{'Net Profit':<25} {net_profit:10.2f}\n"
        report += "="*40 + "\n"

        self.report_textbox.delete("1.0", "end")
        self.report_textbox.insert("1.0", report)

    def generate_gstr1(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        try:
            data = db_manager.get_gstr1_report_data(start_date, end_date)

            report = f"GSTR-1 Summary Report\nFrom {start_date} to {end_date}\n"
            report += "="*80 + "\n\n"

            # B2B Invoices
            report += "B2B Invoices (Registered Customers):\n"
            report += f"{'GSTIN':<16} {'Inv No.':<15} {'Date':<11} {'Value':>12} {'Taxable':>12}\n"
            report += "-"*80 + "\n"
            if data['b2b']:
                for inv in data['b2b']:
                    report += f"{inv['customer_gstin']:<16} {inv['invoice_number']:<15} {inv['invoice_date']:<11} {inv['total_amount']:12.2f} {inv['taxable_amount']:12.2f}\n"
            else:
                report += "No B2B invoices in this period.\n"
            report += "\n" + "="*80 + "\n\n"

            # B2C Summary
            report += "B2C Summary (Unregistered Customers):\n"
            report += f"{'Place of Supply':<20} {'Rate (%)':<10} {'Taxable Value':>18} {'IGST':>12} {'CGST':>12} {'SGST':>12}\n"
            report += "-"*80 + "\n"
            if data['b2c_summary']:
                for summary in data['b2c_summary']:
                    report += f"{summary['place_of_supply']:<20} {summary['total_rate']:<10.2f} {summary['total_taxable_value']:18.2f} {summary['total_igst']:12.2f} {summary['total_cgst']:12.2f} {summary['total_sgst']:12.2f}\n"
            else:
                report += "No B2C sales in this period.\n"

            self.report_textbox.delete("1.0", "end")
            self.report_textbox.insert("1.0", report)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate GSTR-1 report: {e}", parent=self)

    def generate_gstr3b(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        try:
            data = db_manager.get_gstr3b_report_data(start_date, end_date)
            outward = data.get('outward_supplies', {})
            itc = data.get('itc_details', {})

            report = f"GSTR-3B Summary Report\nFrom {start_date} to {end_date}\n"
            report += "="*60 + "\n\n"

            report += "3.1 Details of Outward Supplies and inward supplies liable to reverse charge\n"
            report += "-"*60 + "\n"
            report += f"{'Description':<25} {'Taxable Value':>15} {'IGST':>10} {'CGST':>10} {'SGST':>10}\n"
            report += "-"*60 + "\n"
            report += f"{'(a) Outward taxable supplies':<25} {outward.get('total_taxable', 0):15.2f} {outward.get('total_igst', 0):10.2f} {outward.get('total_cgst', 0):10.2f} {outward.get('total_sgst', 0):10.2f}\n"
            report += "\n" + "="*60 + "\n\n"

            report += "4. Eligible ITC\n"
            report += "-"*60 + "\n"
            report += f"{'Description':<25} {'Taxable Value':>15} {'IGST':>10} {'CGST':>10} {'SGST':>10}\n"
            report += "-"*60 + "\n"
            report += f"{'(A) All other ITC':<25} {itc.get('total_taxable', 0):15.2f} {itc.get('total_igst', 0):10.2f} {itc.get('total_cgst', 0):10.2f} {itc.get('total_sgst', 0):10.2f}\n"

            self.report_textbox.delete("1.0", "end")
            self.report_textbox.insert("1.0", report)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate GSTR-3B report: {e}", parent=self)

    def generate_bs(self):
        as_of_date = self.end_date_entry.get()
        data = db_manager.get_balance_sheet_data(as_of_date)

        # ... (similar logic to generate balance sheet text) ...
        report = f"Balance Sheet\nAs of {as_of_date}\n"
        report += "="*40 + "\n"
        report += "Assets, Liabilities, and Equity calculation not fully implemented in this placeholder."

        self.report_textbox.delete("1.0", "end")
        self.report_textbox.insert("1.0", report)
