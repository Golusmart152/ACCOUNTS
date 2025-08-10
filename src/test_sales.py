import unittest
import os
import sqlite3
from . import db_manager
from db.database_setup import setup_database
import datetime

class TestSales(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for sales tests."""
        cls.db_path = 'db/test_sales_accounting.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean tables before each test."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        tables = [
            "assembly_components", "assemblies", "item_serial_numbers",
            "sales_invoice_items", "sales_invoices", "purchase_invoice_items",
            "purchase_invoices", "suppliers", "customers", "item_batches",
            "items", "godowns", "units", "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()
        self.conn.close()

    def tearDown(self):
        """Close connection after each test."""
        pass

    def _simulate_purchase(self):
        """Helper function to create some inventory to sell."""
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(18, "GST 18%")
        db_manager.add_hsn_code("GPU-HSN", "GPU HSN", 1)
        db_manager.add_godown("Test Store", "Test City")
        db_manager.add_supplier("Test Supplier", "SUPGST", "Sup Address", "111", "sup@email.com", "State")
        db_manager.add_item("Test GPU", 500, 800, 24, 2, "GPU", 1, 1, 1, is_serialized=True)

        purchase_data = {
            "supplier_id": 1, "invoice_number": "PUR-001", "invoice_date": "2023-01-01",
            "total_amount": 1180, "taxable_amount": 1000, "total_gst_amount": 180,
            "igst_amount": 180, "cgst_amount": 0, "sgst_amount": 0, "notes": "Initial stock"
        }
        items_data = [{"item_id": 1, "quantity": 2, "purchase_price": 500, "serial_numbers": ["GPU-SN-01", "GPU-SN-02"], "godown_id": 1}]

        purchase_id = db_manager.create_purchase_invoice_transaction(purchase_data, items_data)
        self.assertIsNotNone(purchase_id)

    def test_create_sale_invoice(self):
        # 1. First, create inventory by simulating a purchase
        self._simulate_purchase()

        # 2. Create a customer
        db_manager.add_customer("Test Customer", "CUSTGST", "Cust Address", "222", "cust@email.com", "Test State", "", "", 0.0)

        # 3. Get available serial numbers for the item we want to sell
        available_serials = db_manager.get_available_serial_numbers_for_item(item_id=1)
        self.assertEqual(len(available_serials), 2)

        serial_to_sell = available_serials[0]

        # 4. Prepare the sales invoice data
        invoice_number = db_manager.get_next_invoice_number()
        self.assertEqual(invoice_number, "INV-0001")

        selling_price = 800
        gst_rate = 18
        gst_amount = selling_price * (gst_rate / 100)
        total_amount = selling_price + gst_amount

        sale_invoice_data = {
            "customer_id": 1, "invoice_number": invoice_number, "invoice_date": datetime.date.today().isoformat(),
            "total_amount": total_amount, "taxable_amount": selling_price, "total_gst_amount": gst_amount,
            "igst_amount": gst_amount, "cgst_amount": 0, "sgst_amount": 0, "notes": "First sale!"
        }

        sale_items_data = [{"item_id": 1, "quantity": 1, "selling_price": selling_price, "serial_ids": [serial_to_sell['id']]}]

        # 5. Run the sales transaction
        sale_id = db_manager.create_sale_invoice_transaction(sale_invoice_data, sale_items_data)

        # 6. Assert the results
        self.assertIsNotNone(sale_id)

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        sn_status = cursor.execute("SELECT status, sale_invoice_id FROM item_serial_numbers WHERE id = ?", (serial_to_sell['id'],)).fetchone()
        self.assertEqual(sn_status['status'], 'SOLD')
        self.assertEqual(sn_status['sale_invoice_id'], sale_id)

        remaining_serials = db_manager.get_available_serial_numbers_for_item(item_id=1)
        self.assertEqual(len(remaining_serials), 1)
        self.assertEqual(remaining_serials[0]['serial_number'], "GPU-SN-02")

        sale_record = cursor.execute("SELECT * FROM sales_invoices WHERE id = ?", (sale_id,)).fetchone()
        self.assertEqual(sale_record['invoice_number'], invoice_number)
        self.assertEqual(sale_record['total_amount'], total_amount)
        conn.close()

if __name__ == '__main__':
    unittest.main()
