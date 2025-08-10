import unittest
import os
import sqlite3
from . import db_manager
from db.database_setup import setup_database
import datetime

class TestPurchasing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database before all tests."""
        cls.db_path = 'db/test_accounting.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean all tables before each individual test."""
        self.conn = sqlite3.connect(db_manager.DATABASE_PATH)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        tables = [
            "assembly_components", "assemblies", "item_serial_numbers",
            "purchase_invoice_items", "purchase_invoices", "suppliers",
            "item_batches", "items", "godowns", "units", "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(18, "GST 18%")
        db_manager.add_gst_slab(5, "GST 5%")
        db_manager.add_hsn_code("123", "CPU HSN", 1)
        db_manager.add_hsn_code("456", "Misc HSN", 2)
        self.conn.close()


    def tearDown(self):
        """Close the connection after each test."""
        pass

    def test_add_and_get_supplier(self):
        self.assertTrue(db_manager.add_supplier("Test Supplier", "GST123", "123 Test St", "555-1234", "test@supplier.com", "State"))
        suppliers = db_manager.get_all_suppliers()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0]['name'], "Test Supplier")

    def test_create_purchase_invoice(self):
        # 1. Setup initial data
        db_manager.add_godown("Main Warehouse", "Main St")
        db_manager.add_supplier("Component King", "CKGST", "456 Tech Rd", "555-5678", "sales@ck.com", "State")
        db_manager.add_item("SuperCPU", 200, 0, 0, 0, "CPU", 1, 1, 1, is_serialized=True)
        db_manager.add_item("Screws", 0.1, 0, 0, 0, "Misc", 1, 2, 2, is_serialized=False)

        # 2. Prepare invoice data
        invoice_data = {
            "supplier_id": 1, "invoice_number": "INV-CK-001", "invoice_date": datetime.date.today().isoformat(),
            "total_amount": 472.525, "taxable_amount": 400.5, "total_gst_amount": 72.025,
            "igst_amount": 72.025, "cgst_amount": 0, "sgst_amount": 0, "notes": "Test purchase"
        }

        items_data = [
            {
                "item_id": 1, "quantity": 2, "purchase_price": 200,
                "taxable_value": 400.0, "total_gst_amount": 72.0,
                "serial_numbers": ["CPU-SN-001", "CPU-SN-002"], "godown_id": 1
            },
            {
                "item_id": 2, "quantity": 5, "purchase_price": 0.1,
                "taxable_value": 0.5, "total_gst_amount": 0.025
            }
        ]

        # 3. Run the transaction
        invoice_id = db_manager.create_purchase_invoice_transaction(invoice_data, items_data)

        # 4. Assert the results
        self.assertIsNotNone(invoice_id)

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        invoice = cursor.execute("SELECT * FROM purchase_invoices WHERE id = ?", (invoice_id,)).fetchone()
        self.assertEqual(invoice['invoice_number'], "INV-CK-001")
        self.assertEqual(invoice['supplier_id'], 1)

        invoice_items = cursor.execute("SELECT * FROM purchase_invoice_items WHERE purchase_invoice_id = ?", (invoice_id,)).fetchall()
        self.assertEqual(len(invoice_items), 2)

        cpu_serials = cursor.execute("SELECT * FROM item_serial_numbers WHERE item_id = 1").fetchall()
        self.assertEqual(len(cpu_serials), 2)

        sn_list = {s['serial_number'] for s in cpu_serials}
        self.assertEqual(sn_list, {"CPU-SN-001", "CPU-SN-002"})

        for sn in cpu_serials:
            self.assertEqual(sn['status'], 'IN_STOCK')
            self.assertEqual(sn['purchase_invoice_id'], invoice_id)
        conn.close()

if __name__ == '__main__':
    unittest.main()
