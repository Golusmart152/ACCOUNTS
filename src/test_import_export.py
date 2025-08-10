import unittest
import os
import csv
from . import db_manager
from db.database_setup import setup_database
from . import csv_generator
from . import csv_validator

class TestImportExport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for all import/export tests."""
        cls.db_path = 'db/test_import_export.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean all relevant tables before each test."""
        self.conn = db_manager.get_db_connection()
        cursor = self.conn.cursor()
        tables = [
            "customers", "suppliers", "items", "godowns", "item_serial_numbers",
            "purchase_invoices", "purchase_invoice_items", "sales_invoices",
            "sales_invoice_items", "job_sheets", "job_sheet_accessories",
            "units", "compound_units", "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(18, "GST 18%")
        db_manager.add_gst_slab(12, "GST 12%")
        db_manager.add_gst_slab(5, "GST 5%")
        db_manager.add_hsn_code("HSN1", "Test HSN 1", 1)
        db_manager.add_hsn_code("HSN2", "Test HSN 2", 2)
        self.conn.close()


    def tearDown(self):
        """Close the connection after each test."""
        pass

    def test_generate_templates(self):
        """Test that all template generation functions create a non-empty file."""
        test_cases = {
            "items": csv_generator.generate_items_template,
            "customers": csv_generator.generate_customers_template,
            "suppliers": csv_generator.generate_suppliers_template,
            "purchases": csv_generator.generate_purchases_template,
        }

        for name, func in test_cases.items():
            with self.subTest(template_name=name):
                filename = f"test_template_{name}.csv"
                success, msg = func(filename)
                self.assertTrue(success)
                self.assertTrue(os.path.exists(filename))
                self.assertGreater(os.path.getsize(filename), 0)
                os.remove(filename)

    def test_export_to_csv(self):
        """Test that data can be exported to a CSV file."""
        db_manager.add_customer("Test Customer", "GST", "Address", "123", "a@b.com", "State", "", "", 0.0)
        customers_data = db_manager.get_customers_for_export()
        self.assertEqual(len(customers_data), 1)

        filename = "test_export.csv"
        success, msg = csv_generator.export_to_csv(customers_data, filename)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(filename))

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            self.assertEqual(len(list(reader)), 2)

        os.remove(filename)

    def test_validate_items_csv_valid_and_invalid(self):
        """Test the item CSV validator with a mix of good and bad data."""
        filename = "test_validate_items.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["name", "hsn_code", "gst_rate", "purchase_price", "selling_price", "default_warranty_months", "minimum_stock_level", "category", "unit_name", "is_serialized"])
            writer.writerow(["Test Item 1", "HSN1", "18", "100", "150", "12", "5", "Cat A", "Pcs", "TRUE"])
            writer.writerow(["", "HSN2", "12", "200", "250", "6", "10", "Cat B", "Pcs", "FALSE"])
            writer.writerow(["Test Item 3", "HSN1", "bad", "300", "350", "24", "2", "Cat C", "Pcs", "1"])
            writer.writerow(["Test Item 4", "HSN2", "5", "400", "450", "0", "0", "Cat D", "Kgs", "0"])

        validated_data, error_msg = csv_validator.validate_items_csv(filename)

        self.assertIsNone(error_msg)
        self.assertEqual(len(validated_data), 4)
        self.assertTrue(validated_data[0]['is_valid'])
        self.assertIn("'name' cannot be empty", validated_data[1]['errors'])
        self.assertIn("'gst_rate' must be a valid number", validated_data[2]['errors'])
        self.assertIn("Unit 'Kgs' does not exist", validated_data[3]['errors'])

        os.remove(filename)

    def test_validate_party_csvs(self):
        """Test validators for simple party CSVs (Customers, Suppliers)."""
        test_cases = {
            "customers": {
                "validator": csv_validator.validate_customers_csv,
                "headers": ["name", "gstin", "address", "phone", "email", "state"],
                "valid_row": ["Cust A", "GST1", "Addr1", "111", "a@c.com", "State1"],
                "invalid_row": ["", "GST2", "Addr2", "222", "b@c.com", "State2"],
            },
            "suppliers": {
                "validator": csv_validator.validate_suppliers_csv,
                "headers": ["name", "gstin", "address", "phone", "email", "state"],
                "valid_row": ["Supp X", "GSTX", "AddrX", "888", "x@s.com", "StateX"],
                "invalid_row": ["", "GSTY", "AddrY", "999", "y@s.com", "StateY"],
            }
        }

        for name, config in test_cases.items():
            with self.subTest(party_type=name):
                filename = f"test_validate_{name}.csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(config['headers'])
                    writer.writerow(config['valid_row'])
                    writer.writerow(config['invalid_row'])

                validated_data, error_msg = config['validator'](filename)
                self.assertIsNone(error_msg)
                self.assertTrue(validated_data[0]['is_valid'])
                self.assertIn("'name' cannot be empty", validated_data[1]['errors'])
                os.remove(filename)

    def test_validate_purchases_csv(self):
        """Test the purchase CSV validator with valid and invalid invoices."""
        db_manager.add_supplier("Supplier A", "", "", "", "", "State")
        db_manager.add_item("Item X", 10, 0, 0, 0, "A", 1, 1, 1, is_serialized=False)
        db_manager.add_item("Item Y (Serialized)", 50, 0, 0, 0, "B", 1, 1, 1, is_serialized=True)

        filename = "test_validate_purchases.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["invoice_number", "supplier_name", "invoice_date", "item_name", "quantity", "purchase_price", "gst_rate", "serial_numbers"])
            writer.writerow(["INV-101", "Supplier A", "2023-01-01", "Item X", "10", "10.0", "18", ""])
            writer.writerow(["INV-101", "Supplier A", "2023-01-01", "Item Y (Serialized)", "2", "50.0", "18", "SN1,SN2"])
            writer.writerow(["INV-102", "Supplier B", "2023-01-02", "Item X", "5", "10.0", "18", ""])
            writer.writerow(["INV-103", "Supplier A", "2023-01-03", "Item Z", "1", "99.0", "5", ""])
            writer.writerow(["INV-104", "Supplier A", "2023-01-04", "Item Y (Serialized)", "2", "50.0", "18", "SN3"])

        validated_data, error_msg = csv_validator.validate_purchases_csv(filename)
        self.assertIsNone(error_msg)
        inv1 = next(i for i in validated_data if i['data']['header']['invoice_number'] == 'INV-101')
        self.assertTrue(inv1['is_valid'])
        inv2 = next(i for i in validated_data if i['data']['header']['invoice_number'] == 'INV-102')
        self.assertIn("Supplier 'Supplier B' not found", inv2['errors'])
        inv3 = next(i for i in validated_data if i['data']['header']['invoice_number'] == 'INV-103')
        self.assertIn("Item 'Item Z' not found", inv3['data']['items'][0]['errors'])
        inv4 = next(i for i in validated_data if i['data']['header']['invoice_number'] == 'INV-104')
        self.assertIn("Number of serials must match quantity", inv4['data']['items'][0]['errors'])
        os.remove(filename)

    def test_import_items_upsert(self):
        """Test the upsert logic for importing items."""
        db_manager.add_item("Existing Item", 10, 10, 0, 0, "Cat E", 1, 1, 1, False)

        import_data = [
            {'data': {'name': 'New Item', 'unit_id': 1, 'hsn_code_id': 2, 'gst_slab_id': 2}, 'is_valid': True},
            {'data': {'name': 'Existing Item', 'purchase_price': 99, 'unit_id': 1, 'hsn_code_id': 1, 'gst_slab_id': 1}, 'is_valid': True},
        ]
        valid_rows = [row['data'] for row in import_data]

        success, inserted, updated, err = db_manager.import_items_from_data(valid_rows)

        self.assertTrue(success)
        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)

        all_items = db_manager.get_all_items()
        self.assertEqual(len(all_items), 2)
        existing_item_updated = next(i for i in all_items if i['name'] == 'Existing Item')
        self.assertEqual(existing_item_updated['purchase_price'], 99)

    def test_import_customers_upsert(self):
        """Test the upsert logic for importing customers."""
        db_manager.add_customer("Old Customer", "", "Old Address", "", "", "", "", "", 0.0)
        import_data = [
            {'data': {'name': 'New Customer', 'phone': '111'}, 'is_valid': True},
            {'data': {'name': 'Old Customer', 'phone': '222'}, 'is_valid': True},
        ]
        valid_rows = [row['data'] for row in import_data]
        success, inserted, updated, err = db_manager.import_customers_from_data(valid_rows)
        self.assertTrue(success)
        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)
        all_cust = db_manager.get_all_customers()
        self.assertEqual(len(all_cust), 2)
        old_cust_updated = next(c for c in all_cust if c['name'] == 'Old Customer')
        self.assertEqual(old_cust_updated['phone'], '222')

    def test_import_suppliers_upsert(self):
        """Test the upsert logic for importing suppliers."""
        db_manager.add_supplier("Old Supplier", "", "Old Address", "", "", "State")
        import_data = [
            {'data': {'name': 'New Supplier', 'email': 'new@s.com', 'state': 'State'}, 'is_valid': True},
            {'data': {'name': 'Old Supplier', 'email': 'old@s.com', 'state': 'State'}, 'is_valid': True},
        ]
        valid_rows = [row['data'] for row in import_data]
        success, inserted, updated, err = db_manager.import_suppliers_from_data(valid_rows)
        self.assertTrue(success)
        self.assertEqual(inserted, 1)
        self.assertEqual(updated, 1)
        all_supp = db_manager.get_all_suppliers()
        self.assertEqual(len(all_supp), 2)
        old_supp_updated = next(s for s in all_supp if s['name'] == 'Old Supplier')
        self.assertEqual(old_supp_updated['email'], 'old@s.com')

    def test_import_purchases(self):
        """Test importing a valid purchase invoice."""
        db_manager.add_supplier("Supplier A", "", "", "", "", "State")
        db_manager.add_item("Item X", 10, 0, 0, 0, "A", 1, 1, 1, False)

        validated_data = [{
            'data': {
                'header': {'invoice_number': 'IMP-001', 'supplier_name': 'Supplier A', 'invoice_date': '2023-01-01'},
                'items': [{'data': {'item_name': 'Item X', 'quantity': '5', 'purchase_price': '10'}}]
            },
            'is_valid': True
        }]

        success, imported_count, err = db_manager.import_purchases_from_data(validated_data)

        self.assertTrue(success, f"Import failed with error: {err}")
        self.assertEqual(imported_count, 1)

        inv = db_manager.get_unpaid_purchase_invoices(1)
        self.assertEqual(len(inv), 1)
        self.assertEqual(inv[0]['invoice_number'], 'IMP-001')

if __name__ == '__main__':
    unittest.main()
