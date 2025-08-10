import unittest
import os
from . import db_manager
from db.database_setup import setup_database
import datetime

class TestSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for search tests."""
        cls.db_path = 'db/test_search.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean tables and populate with test data before each test."""
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        tables = [
            "customers", "suppliers", "items", "godowns", "item_serial_numbers",
            "purchase_invoices", "purchase_invoice_items", "sales_invoices",
            "sales_invoice_items", "job_sheets", "job_sheet_accessories", "units",
            "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        conn.commit()
        conn.close()
        self._populate_test_data()

    def _populate_test_data(self):
        """Helper function to populate the DB with a variety of data."""
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(12, "GST 12%")
        db_manager.add_hsn_code("GP-HSN", "Gamma HSN", 1)
        db_manager.add_customer("Alpha Client", "ACGST123", "Alpha Address", "11111", "alpha@test.com", "State A", "", "", 0.0)
        db_manager.add_supplier("Beta Vendor", "BVGST456", "Beta Address", "22222", "beta@test.com", "State B")
        db_manager.add_item("Gamma Product", 100, 150, 12, 5, "Category G", 1, 1, 1, is_serialized=True)
        db_manager.add_godown("Main Godown", "City Center")

        purchase_data = {
            "supplier_id": 1, "invoice_number": "PINV-BETA-01", "invoice_date": "2023-02-01",
            "total_amount": 112, "taxable_amount": 100, "total_gst_amount": 12,
            "igst_amount": 12, "cgst_amount": 0, "sgst_amount": 0, "notes": ""
        }
        purchase_items = [{"item_id": 1, "quantity": 1, "purchase_price": 100, "serial_numbers": ["DELTA-SN-999"], "godown_id": 1}]
        db_manager.create_purchase_invoice_transaction(purchase_data, purchase_items)

        sale_data = {
            "customer_id": 1, "invoice_number": "INV-ALPHA-01", "invoice_date": "2023-02-15",
            "total_amount": 168, "taxable_amount": 150, "total_gst_amount": 18,
            "igst_amount": 18, "cgst_amount": 0, "sgst_amount": 0, "notes": ""
        }
        sale_items = [{"item_id": 1, "quantity": 1, "selling_price": 150, "serial_ids": [1]}]
        db_manager.create_sale_invoice_transaction(sale_data, sale_items)

        job_sheet_data = {"customer_id": 1, "received_date": "2023-03-01", "product_name": "Epsilon Laptop", "product_serial": "EPSILON-SN-007", "reported_problem": "Won't turn on", "estimated_cost": 50, "estimated_timeline": "3 days", "assigned_to": "Tech 1"}
        db_manager.add_job_sheet(job_sheet_data, ["Charger", "Bag"])


    def test_search_customer(self):
        results = db_manager.universal_search("alpha")
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r['type'] == 'Customer' and r['summary'] == 'Alpha Client' for r in results))
        self.assertTrue(any(r['type'] == 'Sales Invoice' and r['summary'] == 'INV-ALPHA-01' for r in results))

    def test_search_supplier(self):
        results = db_manager.universal_search("beta")
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r['type'] == 'Supplier' and r['summary'] == 'Beta Vendor' for r in results))
        self.assertTrue(any(r['type'] == 'Purchase Invoice' and r['summary'] == 'PINV-BETA-01' for r in results))


    def test_search_item(self):
        results = db_manager.universal_search("gamma")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'Item')
        self.assertEqual(results[0]['summary'], 'Gamma Product')

    def test_search_serial_number(self):
        results = db_manager.universal_search("delta-sn")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'Serial Number')
        self.assertEqual(results[0]['summary'], 'DELTA-SN-999')

    def test_search_sales_invoice(self):
        results = db_manager.universal_search("inv-alpha")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'Sales Invoice')
        self.assertEqual(results[0]['summary'], 'INV-ALPHA-01')

    def test_search_purchase_invoice(self):
        results = db_manager.universal_search("pinv-beta")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'Purchase Invoice')
        self.assertEqual(results[0]['summary'], 'PINV-BETA-01')

    def test_search_job_sheet(self):
        results = db_manager.universal_search("epsilon")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type'], 'Job Sheet')
        self.assertIn('Epsilon Laptop', results[0]['summary'])

    def test_search_no_results(self):
        results = db_manager.universal_search("omega")
        self.assertEqual(len(results), 0)

    def test_search_empty_term(self):
        results = db_manager.universal_search("")
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
