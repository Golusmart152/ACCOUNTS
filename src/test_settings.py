import unittest
import os
from . import db_manager
from db.database_setup import setup_database

class TestSettings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for settings tests."""
        cls.db_path = 'db/test_settings.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean the settings table before each test."""
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM settings;")
        # Also clear invoices to test numbering
        cursor.execute("DELETE FROM sales_invoices;")
        conn.commit()
        conn.close()

    def test_set_and_get_setting(self):
        """Test that a setting can be saved and retrieved."""
        result = db_manager.set_setting("company_name", "Test Corp")
        self.assertTrue(result)

        retrieved = db_manager.get_setting("company_name")
        self.assertEqual(retrieved, "Test Corp")

    def test_get_setting_with_default(self):
        """Test that the default value is returned for a non-existent key."""
        retrieved = db_manager.get_setting("non_existent_key", "default_value")
        self.assertEqual(retrieved, "default_value")

    def test_get_all_settings(self):
        """Test retrieving all settings as a dictionary."""
        db_manager.set_setting("company_name", "Test Corp")
        db_manager.set_setting("company_email", "test@corp.com")

        all_settings = db_manager.get_all_settings()
        self.assertIsInstance(all_settings, dict)
        self.assertEqual(len(all_settings), 2)
        self.assertEqual(all_settings["company_name"], "Test Corp")
        self.assertEqual(all_settings["company_email"], "test@corp.com")

    def test_update_setting(self):
        """Test that setting an existing key updates its value."""
        db_manager.set_setting("company_name", "Initial Name")
        db_manager.set_setting("company_name", "Updated Name")

        retrieved = db_manager.get_setting("company_name")
        self.assertEqual(retrieved, "Updated Name")

    def test_invoice_number_generation_with_settings(self):
        """Test that get_next_invoice_number uses the prefix from settings."""
        # Test with no setting (should use default)
        num1 = db_manager.get_next_invoice_number()
        self.assertEqual(num1, "INV-0001")

        # Add a dummy invoice to advance the number
        conn = db_manager.get_db_connection()
        # Need a customer to satisfy foreign key constraint
        cursor = conn.cursor()
        cursor.execute("INSERT INTO customers (name, state) VALUES ('Test Customer', 'Test State')")
        customer_id = cursor.lastrowid
        conn.commit()

        conn.execute("INSERT INTO sales_invoices (customer_id, invoice_number, invoice_date, total_amount) VALUES (?, 'INV-0001', '2023-01-01', 100);", (customer_id,))
        conn.commit()
        conn.close()

        num2 = db_manager.get_next_invoice_number()
        self.assertEqual(num2, "INV-0002")

        # Now, set a custom prefix
        db_manager.set_setting("prefix_sales_invoice", "TC-")

        # The first number with the new prefix should be 0001
        num3 = db_manager.get_next_invoice_number()
        self.assertEqual(num3, "TC-0001")

if __name__ == '__main__':
    unittest.main()
