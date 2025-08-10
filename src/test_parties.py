import unittest
import os
from . import db_manager
from db.database_setup import setup_database

class TestParties(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for all party tests."""
        cls.db_path = 'db/test_parties.db'
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
            "customers", "suppliers", "sales_invoices", "purchase_invoices",
            "customer_payments", "supplier_payments", "units", "items",
            "hsn_codes", "gst_slabs"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(10, "GST 10%")
        db_manager.add_hsn_code("998877", "Test HSN", 1)
        self.conn.close()


    def tearDown(self):
        """Close the connection after each test."""
        pass

    def test_add_and_update_customer_with_new_fields(self):
        """Test that new customer fields are saved and updated correctly."""
        # Add customer
        add_result = db_manager.add_customer(
            "Test Customer", "GST123", "Addr 1", "111", "t@c.com", "State A",
            "Bill Addr", "Ship Addr", 5000.0
        )
        self.assertTrue(add_result)

        # Verify
        customers = db_manager.get_all_customers()
        self.assertEqual(len(customers), 1)
        cust = customers[0]
        self.assertEqual(cust['billing_address'], "Bill Addr")
        self.assertEqual(cust['credit_limit'], 5000.0)

        # Update customer
        update_result = db_manager.update_customer(
            cust['id'], "Test Customer", "GST123", "Addr 1", "111", "t@c.com", "State A",
            "New Bill Addr", "New Ship Addr", 10000.0
        )
        self.assertTrue(update_result)

        # Verify update
        customers = db_manager.get_all_customers()
        self.assertEqual(len(customers), 1)
        cust_updated = customers[0]
        self.assertEqual(cust_updated['billing_address'], "New Bill Addr")
        self.assertEqual(cust_updated['credit_limit'], 10000.0)

    def test_get_transactions_for_customer(self):
        """Test fetching a customer's transaction ledger."""
        db_manager.add_customer("Ledger Customer", "", "", "", "", "", "", "", 0.0)
        db_manager.add_item("Test Item", 100, 150, 0, 0, "Default", 1, 1, 1)
        invoice_data = {
            "customer_id": 1, "invoice_number": "INV-01", "invoice_date": "2023-01-10",
            "total_amount": 165, "taxable_amount": 150, "total_gst_amount": 15,
            "igst_amount": 15, "cgst_amount": 0, "sgst_amount": 0, "notes": ""
        }
        items_data = [{"item_id": 1, "quantity": 1, "selling_price": 150}]
        db_manager.create_sale_invoice_transaction(invoice_data, items_data)
        db_manager.record_customer_payment(1, "2023-01-15", 500, [(1, 165)])

        transactions = db_manager.get_transactions_for_customer(1)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['type'], 'Sales Invoice')
        self.assertEqual(transactions[1]['type'], 'Payment Received')
        self.assertEqual(transactions[0]['debit'], 165)
        self.assertEqual(transactions[1]['credit'], 500)

    def test_get_account_statement_data(self):
        """Test the data retrieval for an account statement."""
        db_manager.add_customer("Statement Customer", "", "", "", "", "", "", "", 0.0)
        db_manager.add_item("Test Item", 100, 150, 0, 0, "Default", 1, 1, 1)

        # Transaction before the statement period (for opening balance)
        db_manager.create_sale_invoice_transaction(
            {"customer_id": 1, "invoice_number": "INV-01", "invoice_date": "2022-12-20", "total_amount": 550, "taxable_amount": 500, "total_gst_amount": 50, "igst_amount": 50, "cgst_amount": 0, "sgst_amount": 0, "notes": ""},
            [{"item_id": 1, "quantity": 1, "selling_price": 500}]
        )
        # Transactions within the statement period
        db_manager.create_sale_invoice_transaction(
            {"customer_id": 1, "invoice_number": "INV-02", "invoice_date": "2023-01-10", "total_amount": 1100, "taxable_amount": 1000, "total_gst_amount": 100, "igst_amount": 100, "cgst_amount": 0, "sgst_amount": 0, "notes": ""},
            [{"item_id": 1, "quantity": 1, "selling_price": 1000}]
        )
        db_manager.record_customer_payment(1, "2023-01-15", 300, [(2, 300)])
        # Transaction after the statement period
        db_manager.create_sale_invoice_transaction(
            {"customer_id": 1, "invoice_number": "INV-03", "invoice_date": "2023-02-05", "total_amount": 220, "taxable_amount": 200, "total_gst_amount": 20, "igst_amount": 20, "cgst_amount": 0, "sgst_amount": 0, "notes": ""},
            [{"item_id": 1, "quantity": 1, "selling_price": 200}]
        )

        opening_balance, transactions = db_manager.get_account_statement_data(1, 'Customer', '2023-01-01', '2023-01-31')

        self.assertAlmostEqual(opening_balance, 550.0)
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]['document_number'], 'INV-02')
        self.assertEqual(transactions[1]['type'], 'Payment Received')

if __name__ == '__main__':
    unittest.main()
