import unittest
import os
import sqlite3
from . import db_manager
from db.database_setup import setup_database

class TestAccounting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a clean database for accounting tests."""
        cls.db_path = 'db/test_accounting_final.db'
        db_manager.DATABASE_PATH = cls.db_path
        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)
        setup_database(db_path=cls.db_path)
        db_manager.initialize_chart_of_accounts()

    def setUp(self):
        """Clean transaction tables and setup default entities before each test."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        tables = [
            "gl_entries", "gl_transactions", "customer_payment_allocations",
            "supplier_payment_allocations", "customer_payments", "supplier_payments",
            "sales_invoice_items", "purchase_invoice_items", "sales_invoices",
            "purchase_invoices", "item_serial_numbers", "items", "customers",
            "suppliers", "godowns", "hsn_codes", "gst_slabs", "units"
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
        self.conn.commit()

        # Get account IDs for use in tests
        self.accounts = {acc['name']: acc['id'] for acc in db_manager.get_all_accounts()}

        # Setup default data needed for tests
        db_manager.add_unit("Pcs")
        db_manager.add_gst_slab(10, "GST 10%")
        db_manager.add_hsn_code("1234", "Test HSN", 1)
        self.conn.close()


    def _get_gl_balance(self, account_name):
        """Helper to get the debit/credit balance of an account."""
        conn = db_manager.get_db_connection()
        acc_id = self.accounts[account_name]
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(debit), SUM(credit) FROM gl_entries WHERE account_id = ?", (acc_id,))
        result = cursor.fetchone()
        conn.close()
        debits = result[0] or 0
        credits = result[1] or 0
        return debits - credits

    def test_purchase_gl_entries(self):
        # 1. Setup
        db_manager.add_supplier("Test Supplier", "", "", "", "", "State")
        db_manager.add_item("Test Item", 100, 150, 0, 0, "Default", 1, 1, 1)
        invoice_data = {
            "supplier_id": 1, "invoice_number": "P-001", "invoice_date": "2023-01-01",
            "total_amount": 110, "taxable_amount": 100, "total_gst_amount": 10,
            "cgst_amount": 0, "sgst_amount": 0, "igst_amount": 10, "notes": ""
        }
        items_data = [{"item_id": 1, "quantity": 1, "purchase_price": 100, "taxable_value": 100, "total_gst_amount": 10}]

        # 2. Action
        db_manager.create_purchase_invoice_transaction(invoice_data, items_data)

        # 3. Assert
        self.assertAlmostEqual(self._get_gl_balance('Inventory'), 100)
        self.assertAlmostEqual(self._get_gl_balance('GST Payable'), 10)
        self.assertAlmostEqual(self._get_gl_balance('Accounts Payable'), -110)

    def test_sale_gl_entries(self):
        # 1. Setup
        db_manager.add_item("Test Item", 100, 150, 0, 0, "Default", 1, 1, 1)
        db_manager.add_customer("Test Customer", "", "", "", "", "", "", "", 0.0)
        invoice_data = {
            "customer_id": 1, "invoice_number": "S-001", "invoice_date": "2023-01-02",
            "total_amount": 165, "taxable_amount": 150, "total_gst_amount": 15,
            "cgst_amount": 0, "sgst_amount": 0, "igst_amount": 15, "notes": ""
        }
        items_data = [{"item_id": 1, "quantity": 1, "selling_price": 150, "taxable_value": 150, "total_gst_amount": 15}]

        # 2. Action
        db_manager.create_sale_invoice_transaction(invoice_data, items_data)

        # 3. Assert
        self.assertAlmostEqual(self._get_gl_balance('Accounts Receivable'), 165)
        self.assertAlmostEqual(self._get_gl_balance('Sales Revenue'), -150)
        self.assertAlmostEqual(self._get_gl_balance('GST Payable'), -15)
        self.assertAlmostEqual(self._get_gl_balance('Cost of Goods Sold'), 100)
        self.assertAlmostEqual(self._get_gl_balance('Inventory'), -100)

    def test_customer_payment_gl_entries(self):
        # 1. Setup (a sale must exist first)
        self.test_sale_gl_entries()

        # 2. Action
        db_manager.record_customer_payment(customer_id=1, payment_date="2023-01-03", amount=165, allocations=[(1, 165)])

        # 3. Assert
        self.assertAlmostEqual(self._get_gl_balance('Cash'), 165)
        # AR was 165, now it's paid, so balance should be 0
        self.assertAlmostEqual(self._get_gl_balance('Accounts Receivable'), 0)

    def test_bank_reconciliation(self):
        # 1. Setup: Create a customer payment, which is a cash transaction
        self.test_customer_payment_gl_entries()

        # 2. Action & Pre-Assert
        unreconciled = db_manager.get_unreconciled_cash_transactions()
        self.assertEqual(len(unreconciled), 1)
        self.assertEqual(unreconciled[0]['description'], 'Payment from customer ID 1')

        # 3. Reconcile the transaction
        transaction_id_to_reconcile = unreconciled[0]['id']
        recon_date = "2023-01-04"
        self.assertTrue(db_manager.mark_transactions_as_reconciled([transaction_id_to_reconcile], recon_date))

        # 4. Assert final state
        unreconciled_after = db_manager.get_unreconciled_cash_transactions()
        self.assertEqual(len(unreconciled_after), 0)

        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        reconciled_tran = cursor.execute("SELECT * FROM gl_transactions WHERE id = ?", (transaction_id_to_reconcile,)).fetchone()
        conn.close()
        self.assertTrue(reconciled_tran['is_reconciled'])
        self.assertEqual(reconciled_tran['reconciliation_date'], recon_date)

if __name__ == '__main__':
    unittest.main()
