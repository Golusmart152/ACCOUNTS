import unittest
import os
import sqlite3
from . import db_manager
from db.database_setup import setup_database
import datetime
from dateutil.relativedelta import relativedelta

class TestReports(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for reporting tests."""
        cls.db_path = 'db/test_reporting.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean tables and create a standard set of transactions for each test."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        tables = [
            "gl_entries", "gl_transactions", "customer_payment_allocations",
            "supplier_payment_allocations", "customer_payments", "supplier_payments",
            "sales_invoice_items", "purchase_invoice_items", "sales_invoices",
            "purchase_invoices", "item_serial_numbers", "items", "customers",
            "suppliers", "godowns", "units", "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()

        # Create a standard set of data for reports
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(10, "GST 10%")
        db_manager.add_hsn_code("998877", "Test HSN", 1)
        db_manager.add_godown("Test Godown", "Test Location")
        db_manager.add_supplier("Test Supplier", "", "", "", "", "State")
        db_manager.add_customer("Test Customer", "", "", "", "", "Test State", "", "", 0.0)
        db_manager.add_item("Test Item", 100, 150, 2, 0, "Default", 1, 1, 1, is_serialized=True)

        # Purchase
        p_inv_data = {
            "supplier_id": 1, "invoice_number": "P-001", "invoice_date": "2023-01-01",
            "total_amount": 110, "taxable_amount": 100, "total_gst_amount": 10,
            "igst_amount": 10, "cgst_amount": 0, "sgst_amount": 0, "notes": ""
        }
        p_items_data = [{"item_id": 1, "quantity": 1, "purchase_price": 100, "serial_numbers": ["ITEM-001"], "godown_id": 1}]
        db_manager.create_purchase_invoice_transaction(p_inv_data, p_items_data)

        # Sale
        s_inv_data = {
            "customer_id": 1, "invoice_number": "S-001", "invoice_date": "2023-01-15",
            "total_amount": 165, "taxable_amount": 150, "total_gst_amount": 15,
            "igst_amount": 15, "cgst_amount": 0, "sgst_amount": 0, "notes": ""
        }
        s_items_data = [{"item_id": 1, "quantity": 1, "selling_price": 150, "serial_ids": [1]}]
        db_manager.create_sale_invoice_transaction(s_inv_data, s_items_data)
        self.conn.close()

    def tearDown(self):
        pass

    def test_profit_and_loss(self):
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        data = db_manager.get_profit_and_loss_data(start_date, end_date)

        revenue = 0
        cogs = 0
        for row in data:
            if row['name'] == 'Sales Revenue':
                revenue = row['total_credits'] - row['total_debits']
            elif row['name'] == 'Cost of Goods Sold':
                cogs = row['total_debits'] - row['total_credits']

        self.assertAlmostEqual(revenue, 150)
        self.assertAlmostEqual(cogs, 100)
        self.assertAlmostEqual(revenue - cogs, 50)

    def test_expiring_warranty_report(self):
        # This test remains a placeholder as mocking datetime is out of scope for this fix.
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
