import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

DATABASE_PATH = '../db/accounting.db'

# --- Connection ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Settings ---
def get_setting(key, default=None):
    """Gets a setting value from the database."""
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if row:
        return row['value']
    return default

def set_setting(key, value):
    """Saves a setting value to the database."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def get_all_settings():
    """Gets all settings from the database as a dictionary."""
    conn = get_db_connection()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}


# --- Data Management ---
import shutil

# --- GST Management ---
def get_all_gst_slabs():
    """Gets all GST slabs from the database."""
    conn = get_db_connection()
    slabs = conn.execute("SELECT id, rate, description FROM gst_slabs ORDER BY rate").fetchall()
    conn.close()
    return [dict(row) for row in slabs]

def add_gst_slab(rate, description):
    """Adds a new GST slab."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO gst_slabs (rate, description) VALUES (?, ?)", (rate, description))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error on adding GST slab: {e}")
        # Re-raise the exception so the UI layer can catch it for specific error handling
        raise e
    finally:
        conn.close()

def delete_gst_slab(slab_id):
    """Deletes a GST slab by its ID."""
    conn = get_db_connection()
    try:
        # We should also check if this slab is being used by any items.
        # For now, we'll just delete it. A more robust implementation would prevent this.
        conn.execute("DELETE FROM gst_slabs WHERE id = ?", (slab_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error on deleting GST slab: {e}")
        raise e
    finally:
        conn.close()

# --- HSN Management ---
def get_all_hsn_codes_with_details():
    """Gets all HSN codes with their associated GST slab rate for display."""
    conn = get_db_connection()
    query = """
    SELECT
        h.id,
        h.hsn_code,
        h.description,
        g.rate as gst_rate,
        h.gst_slab_id
    FROM hsn_codes h
    LEFT JOIN gst_slabs g ON h.gst_slab_id = g.id
    ORDER BY h.hsn_code
    """
    codes = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in codes]

def add_hsn_code(code, description, gst_slab_id):
    """Adds a new HSN code."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO hsn_codes (hsn_code, description, gst_slab_id) VALUES (?, ?, ?)",
                     (code, description, gst_slab_id))
        conn.commit()
    except sqlite3.Error as e:
        raise e # Re-raise to be handled by UI
    finally:
        conn.close()

def update_hsn_code(hsn_id, code, description, gst_slab_id):
    """Updates an existing HSN code."""
    conn = get_db_connection()
    try:
        conn.execute("UPDATE hsn_codes SET hsn_code = ?, description = ?, gst_slab_id = ? WHERE id = ?",
                     (code, description, gst_slab_id, hsn_id))
        conn.commit()
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()

def delete_hsn_code(hsn_id):
    """Deletes an HSN code."""
    conn = get_db_connection()
    # First, check if the HSN code is in use
    in_use = conn.execute("SELECT 1 FROM items WHERE hsn_code_id = ?", (hsn_id,)).fetchone()
    if in_use:
        raise ValueError("This HSN code is assigned to one or more items and cannot be deleted.")

    try:
        conn.execute("DELETE FROM hsn_codes WHERE id = ?", (hsn_id,))
        conn.commit()
    except sqlite3.Error as e:
        raise e
    finally:
        conn.close()


# --- Unit Management ---
def add_unit(name):
    """Adds a new simple unit."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO units (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # For UNIQUE constraint
        return False
    finally:
        conn.close()

def get_all_units():
    """Gets all simple units from the database."""
    conn = get_db_connection()
    units = conn.execute("SELECT * FROM units ORDER BY name").fetchall()
    conn.close()
    return units

def add_compound_unit(base_unit_id, secondary_unit_id, conversion_factor):
    """Adds a new compound unit relationship."""
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO compound_units (base_unit_id, secondary_unit_id, conversion_factor) VALUES (?, ?, ?)",
                     (base_unit_id, secondary_unit_id, conversion_factor))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error on adding compound unit: {e}")
        return False
    finally:
        conn.close()

def get_all_compound_units_display():
    """Gets all compound units with names for display purposes."""
    conn = get_db_connection()
    query = """
    SELECT
        cu.id,
        bu.name as base_unit_name,
        su.name as secondary_unit_name,
        cu.conversion_factor
    FROM compound_units cu
    JOIN units bu ON cu.base_unit_id = bu.id
    JOIN units su ON cu.secondary_unit_id = su.id
    ORDER BY base_unit_name, secondary_unit_name
    """
    compound_units = conn.execute(query).fetchall()
    conn.close()
    return compound_units

def get_units_for_item(item_id):
    """
    Gets all available transaction units for a given item, including the base
    unit and any larger units defined in compound relationships.
    Returns a list of dicts, e.g., [{'name': 'Pcs', 'factor': 1.0}, {'name': 'Box', 'factor': 100.0}]
    """
    conn = get_db_connection()

    # Get the item's base unit ID and name
    item_unit_row = conn.execute("SELECT unit_id, u.name as unit_name FROM items i JOIN units u ON i.unit_id = u.id WHERE i.id = ?", (item_id,)).fetchone()
    if not item_unit_row or not item_unit_row['unit_id']:
        conn.close()
        return []

    base_unit_id = item_unit_row['unit_id']
    base_unit_name = item_unit_row['unit_name']

    # The base unit itself is always an option, with a factor of 1
    available_units = [{'name': base_unit_name, 'factor': 1.0}]

    # Find all compound units that are defined in terms of this item's base unit
    compound_units_rows = conn.execute("""
        SELECT
            bu.name,
            cu.conversion_factor
        FROM compound_units cu
        JOIN units bu ON cu.base_unit_id = bu.id
        WHERE cu.secondary_unit_id = ?
    """, (base_unit_id,)).fetchall()

    conn.close()

    for row in compound_units_rows:
        available_units.append({'name': row['name'], 'factor': row['conversion_factor']})

    return available_units


def backup_database(backup_file_path):
    """Copies the current database file to the specified backup path."""
    try:
        shutil.copyfile(DATABASE_PATH, backup_file_path)
        return True
    except (IOError, shutil.Error) as e:
        print(f"Error backing up database: {e}")
        return False

def restore_database(backup_file_path):
    """Restores the database from a backup file."""
    try:
        shutil.copyfile(backup_file_path, DATABASE_PATH)
        return True
    except (IOError, shutil.Error) as e:
        print(f"Error restoring database: {e}")
        return False


# --- GL & Accounts ---
def initialize_chart_of_accounts():
    conn = get_db_connection()
    cursor = conn.cursor()
    accounts = [
        ('Cash', 'Asset', True), ('Accounts Receivable', 'Asset', True), ('Inventory', 'Asset', True),
        ('Accounts Payable', 'Liability', True), ('GST Payable', 'Liability', True),
        ('Owner\'s Equity', 'Equity', True), ('Sales Revenue', 'Revenue', True),
        ('Cost of Goods Sold', 'Expense', True)
    ]
    try:
        cursor.executemany("INSERT INTO accounts (name, type, is_predefined) VALUES (?, ?, ?)", accounts)
        conn.commit()
    except sqlite3.IntegrityError: pass
    finally: conn.close()

def get_all_accounts():
    conn = get_db_connection()
    accounts = conn.execute("SELECT * FROM accounts ORDER BY type, name").fetchall()
    conn.close()
    return accounts

# --- Entity Management ---
def add_godown(name, location):
    conn = get_db_connection()
    try: conn.execute("INSERT INTO godowns (name, location) VALUES (?, ?)", (name, location)); conn.commit(); return True
    except: return False
    finally: conn.close()

def get_all_godowns():
    conn = get_db_connection()
    godowns = conn.execute("SELECT * FROM godowns ORDER BY name").fetchall()
    conn.close()
    return godowns

def update_godown(godown_id, name, location):
    conn = get_db_connection()
    try: conn.execute("UPDATE godowns SET name = ?, location = ? WHERE id = ?", (name, location, godown_id)); conn.commit(); return True
    except: return False
    finally: conn.close()

def add_item(name, purchase_price, selling_price, warranty, min_stock, category, unit_id, hsn_code_id, gst_slab_id, is_serialized=False):
    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO items (name, purchase_price, selling_price, default_warranty_months,
                               minimum_stock_level, category, unit_id, hsn_code_id, gst_slab_id, is_serialized)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, purchase_price, selling_price, warranty, min_stock, category, unit_id, hsn_code_id, gst_slab_id, is_serialized))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"DB Error on add_item: {e}")
        return False
    finally:
        conn.close()

def update_item(item_id, name, purchase_price, selling_price, warranty, min_stock, category, unit_id, hsn_code_id, gst_slab_id, is_serialized=False):
    conn = get_db_connection()
    try:
        conn.execute("""
            UPDATE items SET name=?, purchase_price=?, selling_price=?, default_warranty_months=?,
                            minimum_stock_level=?, category=?, unit_id=?, hsn_code_id=?, gst_slab_id=?, is_serialized=?
            WHERE id=?
        """, (name, purchase_price, selling_price, warranty, min_stock, category, unit_id, hsn_code_id, gst_slab_id, is_serialized, item_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"DB Error on update_item: {e}")
        return False
    finally:
        conn.close()

def get_all_items():
    conn = get_db_connection()
    query = """
    SELECT
        i.id, i.name, i.category, u.name as unit_name,
        i.purchase_price, i.selling_price, i.default_warranty_months,
        i.minimum_stock_level, i.is_serialized, i.is_assembled_item,
        h.hsn_code, g.rate as gst_rate,
        i.hsn_code_id, i.gst_slab_id, i.unit_id
    FROM items i
    LEFT JOIN units u ON i.unit_id = u.id
    LEFT JOIN hsn_codes h ON i.hsn_code_id = h.id
    LEFT JOIN gst_slabs g ON i.gst_slab_id = g.id
    ORDER BY i.name
    """
    items = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in items]

def add_supplier(name, gstin, address, phone, email, state):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO suppliers (name, gstin, address, phone, email, state) VALUES (?, ?, ?, ?, ?, ?)", (name, gstin, address, phone, email, state))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_all_suppliers():
    conn = get_db_connection()
    suppliers = conn.execute("SELECT * FROM suppliers ORDER BY name").fetchall()
    conn.close()
    return suppliers

def update_supplier(supplier_id, name, gstin, address, phone, email, state):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE suppliers SET name = ?, gstin = ?, address = ?, phone = ?, email = ?, state = ? WHERE id = ?", (name, gstin, address, phone, email, state, supplier_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def add_customer(name, gstin, address, phone, email, state, billing_address, shipping_address, credit_limit):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO customers (name, gstin, address, phone, email, state, billing_address, shipping_address, credit_limit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (name, gstin, address, phone, email, state, billing_address, shipping_address, credit_limit))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_all_customers():
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return customers

def update_customer(customer_id, name, gstin, address, phone, email, state, billing_address, shipping_address, credit_limit):
    conn = get_db_connection()
    try:
        conn.execute("UPDATE customers SET name=?, gstin=?, address=?, phone=?, email=?, state=?, billing_address=?, shipping_address=?, credit_limit=? WHERE id=?",
                     (name, gstin, address, phone, email, state, billing_address, shipping_address, credit_limit, customer_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# --- Party Ledger Functions ---
def get_transactions_for_customer(customer_id):
    """Fetches a chronological list of invoices and payments for a customer."""
    conn = get_db_connection()
    query = """
    SELECT date, type, document_number, debit, credit FROM (
        SELECT invoice_date as date, 'Sales Invoice' as type, invoice_number as document_number, total_amount as debit, 0 as credit FROM sales_invoices WHERE customer_id = ?
        UNION ALL
        SELECT payment_date as date, 'Payment Received' as type, 'Payment ID ' || id as document_number, 0 as debit, amount as credit FROM customer_payments WHERE customer_id = ?
    ) ORDER BY date
    """
    transactions = conn.execute(query, (customer_id, customer_id)).fetchall()
    conn.close()
    return transactions

def get_transactions_for_supplier(supplier_id):
    """Fetches a chronological list of invoices and payments for a supplier."""
    conn = get_db_connection()
    query = """
    SELECT date, type, document_number, debit, credit FROM (
        SELECT invoice_date as date, 'Purchase Invoice' as type, invoice_number as document_number, total_amount as debit, 0 as credit FROM purchase_invoices WHERE supplier_id = ?
        UNION ALL
        SELECT payment_date as date, 'Payment Made' as type, 'Payment ID ' || id as document_number, 0 as debit, amount as credit FROM supplier_payments WHERE supplier_id = ?
    ) ORDER BY date
    """
    transactions = conn.execute(query, (supplier_id, supplier_id)).fetchall()
    conn.close()
    return transactions

def get_account_statement_data(party_id, party_type, start_date, end_date):
    """Fetches data for a party's account statement, including opening balance."""
    conn = get_db_connection()
    opening_balance = 0.0

    if party_type == 'Customer':
        ob_query = """
        SELECT SUM(debit) - SUM(credit) FROM (
            SELECT total_amount as debit, 0 as credit FROM sales_invoices WHERE customer_id = ? AND invoice_date < ?
            UNION ALL
            SELECT 0 as debit, amount as credit FROM customer_payments WHERE customer_id = ? AND payment_date < ?
        )
        """
        ob_result = conn.execute(ob_query, (party_id, start_date, party_id, start_date)).fetchone()
        opening_balance = ob_result[0] if ob_result and ob_result[0] is not None else 0.0

        trans_query = """
        SELECT date, type, document_number, debit, credit FROM (
            SELECT invoice_date as date, 'Sales Invoice' as type, invoice_number as document_number, total_amount as debit, 0 as credit FROM sales_invoices WHERE customer_id = ? AND invoice_date BETWEEN ? AND ?
            UNION ALL
            SELECT payment_date as date, 'Payment Received' as type, 'Payment ID ' || id as document_number, 0 as debit, amount as credit FROM customer_payments WHERE customer_id = ? AND payment_date BETWEEN ? AND ?
        ) ORDER BY date
        """
        transactions = conn.execute(trans_query, (party_id, start_date, end_date, party_id, start_date, end_date)).fetchall()

    else: # Supplier
        ob_query = """
        SELECT SUM(credit) - SUM(debit) FROM (
            SELECT total_amount as credit, 0 as debit FROM purchase_invoices WHERE supplier_id = ? AND invoice_date < ?
            UNION ALL
            SELECT 0 as credit, amount as debit FROM supplier_payments WHERE supplier_id = ? AND payment_date < ?
        )
        """
        ob_result = conn.execute(ob_query, (party_id, start_date, party_id, start_date)).fetchone()
        opening_balance = ob_result[0] if ob_result and ob_result[0] is not None else 0.0

        trans_query = """
        SELECT date, type, document_number, debit, credit FROM (
            SELECT invoice_date as date, 'Purchase Invoice' as type, invoice_number as document_number, 0 as debit, total_amount as credit FROM purchase_invoices WHERE supplier_id = ? AND invoice_date BETWEEN ? AND ?
            UNION ALL
            SELECT payment_date as date, 'Payment Made' as type, 'Payment ID ' || id as document_number, amount as debit, 0 as credit FROM supplier_payments WHERE supplier_id = ? AND payment_date BETWEEN ? AND ?
        ) ORDER BY date
        """
        transactions = conn.execute(trans_query, (party_id, start_date, end_date, party_id, start_date, end_date)).fetchall()

    conn.close()
    return opening_balance, transactions

# --- Invoice & Payment Queries ---
def get_next_invoice_number():
    """
    Generates the next sales invoice number based on the prefix from settings
    and the last used number for that prefix.
    """
    conn = get_db_connection()
    prefix = get_setting("prefix_sales_invoice", "INV-")

    last_invoice = conn.execute(
        "SELECT invoice_number FROM sales_invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}%",)
    ).fetchone()
    conn.close()

    if last_invoice:
        try:
            numeric_part = last_invoice['invoice_number'][len(prefix):]
            next_number = int(numeric_part) + 1
            return f"{prefix}{next_number:04d}"
        except (ValueError, TypeError):
            return f"{prefix}0001"
    else:
        return f"{prefix}0001"

def get_available_serial_numbers_for_item(item_id):
    conn = get_db_connection()
    serials = conn.execute("SELECT id, serial_number FROM item_serial_numbers WHERE item_id = ? AND status = 'IN_STOCK'", (item_id,)).fetchall()
    conn.close()
    return serials

def get_in_stock_serial_numbers():
    conn = get_db_connection()
    components = conn.execute("SELECT sn.id as serial_id, sn.serial_number, i.id as item_id, i.name as item_name, i.purchase_price FROM item_serial_numbers sn JOIN items i ON sn.item_id = i.id WHERE sn.status = 'IN_STOCK' AND i.is_assembled_item = FALSE ORDER BY i.name, sn.serial_number").fetchall()
    conn.close()
    return components

def get_unpaid_sales_invoices(customer_id):
    conn = get_db_connection()
    invoices = conn.execute("SELECT id, invoice_number, invoice_date, total_amount, amount_paid, status FROM sales_invoices WHERE customer_id = ? AND status != 'PAID' ORDER BY invoice_date", (customer_id,)).fetchall()
    conn.close()
    return invoices

def get_unpaid_purchase_invoices(supplier_id):
    conn = get_db_connection()
    invoices = conn.execute("SELECT id, invoice_number, invoice_date, total_amount, amount_paid, status FROM purchase_invoices WHERE supplier_id = ? AND status != 'PAID' ORDER BY invoice_date", (supplier_id,)).fetchall()
    conn.close()
    return invoices

def get_unreconciled_cash_transactions():
    conn = get_db_connection()
    cash_account_id = conn.execute("SELECT id FROM accounts WHERE name = 'Cash'").fetchone()['id']
    transactions = conn.execute("SELECT gt.id, gt.date, gt.description, ge.debit, ge.credit FROM gl_transactions gt JOIN gl_entries ge ON gt.id = ge.transaction_id WHERE ge.account_id = ? AND gt.is_reconciled = FALSE ORDER BY gt.date", (cash_account_id,)).fetchall()
    conn.close()
    return transactions

# --- Transactional Operations ---
def create_gl_transaction(conn, description, date, entries, source_doc_type=None, source_doc_id=None):
    cursor = conn.cursor()
    total_debits = sum(e[1] for e in entries if e[1] is not None)
    total_credits = sum(e[2] for e in entries if e[2] is not None)
    if round(total_debits, 2) != round(total_credits, 2): raise ValueError("Debits do not equal credits.")
    cursor.execute("INSERT INTO gl_transactions (date, description, source_doc_type, source_doc_id) VALUES (?, ?, ?, ?)", (date, description, source_doc_type, source_doc_id))
    transaction_id = cursor.lastrowid
    for account_id, debit, credit in entries:
        cursor.execute("INSERT INTO gl_entries (transaction_id, account_id, debit, credit) VALUES (?, ?, ?, ?)", (transaction_id, account_id, debit, credit))
    return transaction_id

def create_purchase_invoice_transaction(invoice_data, items_data, conn_override=None):
    conn = conn_override if conn_override else get_db_connection()

    def _execute_transaction(c):
        cursor = c.cursor()
        accounts = {name: id for id, name in cursor.execute("SELECT id, name FROM accounts WHERE name IN ('Inventory', 'Accounts Payable', 'GST Payable')").fetchall()}

        cursor.execute("""
            INSERT INTO purchase_invoices (supplier_id, invoice_number, invoice_date, total_amount, taxable_amount, cgst_amount, sgst_amount, igst_amount, total_gst_amount, notes, status, amount_paid)
            VALUES (:supplier_id, :invoice_number, :invoice_date, :total_amount, :taxable_amount, :cgst_amount, :sgst_amount, :igst_amount, :total_gst_amount, :notes, 'UNPAID', 0.0)
        """, invoice_data)
        purchase_invoice_id = cursor.lastrowid

        gl_desc = f"Purchase from supp ID {invoice_data['supplier_id']}, Inv #{invoice_data['invoice_number']}"
        gl_entries = [
            (accounts['Inventory'], invoice_data.get('taxable_amount', 0), None),
            (accounts['GST Payable'], invoice_data.get('total_gst_amount', 0), None),
            (accounts['Accounts Payable'], None, invoice_data.get('total_amount', 0))
        ]
        create_gl_transaction(c, gl_desc, invoice_data['invoice_date'], gl_entries, 'PURCHASE', purchase_invoice_id)

        for item in items_data:
            cursor.execute("""
                INSERT INTO purchase_invoice_items (purchase_invoice_id, item_id, quantity, purchase_price, taxable_value, cgst_rate, sgst_rate, igst_rate, cgst_amount, sgst_amount, igst_amount, total_gst_amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (purchase_invoice_id, item['item_id'], item['quantity'], item['purchase_price'], item.get('taxable_value', 0), item.get('cgst_rate', 0), item.get('sgst_rate', 0), item.get('igst_rate', 0), item.get('cgst_amount', 0), item.get('sgst_amount', 0), item.get('igst_amount', 0), item.get('total_gst_amount', 0)))
            if item.get('serial_numbers'):
                for sn in item['serial_numbers']:
                    cursor.execute("INSERT INTO item_serial_numbers (item_id, serial_number, status, godown_id, purchase_invoice_id) VALUES (?, ?, 'IN_STOCK', ?, ?)", (item['item_id'], sn, item['godown_id'], purchase_invoice_id))
        return purchase_invoice_id

    try:
        if conn_override:
            return _execute_transaction(conn)
        else:
            with conn:
                return _execute_transaction(conn)
    except (sqlite3.Error, ValueError) as e:
        print(f"Error creating purchase invoice: {e}")
        return None
    finally:
        if not conn_override and conn:
            conn.close()

def create_sale_invoice_transaction(invoice_data, items_data):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            accounts = {name: id for id, name in cursor.execute("SELECT id, name FROM accounts WHERE name IN ('Accounts Receivable', 'Sales Revenue', 'GST Payable', 'Cost of Goods Sold', 'Inventory')").fetchall()}

            cursor.execute("""
                INSERT INTO sales_invoices (customer_id, invoice_number, invoice_date, total_amount, taxable_amount, cgst_amount, sgst_amount, igst_amount, total_gst_amount, notes, status, amount_paid)
                VALUES (:customer_id, :invoice_number, :invoice_date, :total_amount, :taxable_amount, :cgst_amount, :sgst_amount, :igst_amount, :total_gst_amount, :notes, 'UNPAID', 0.0)
            """, invoice_data)
            sale_invoice_id = cursor.lastrowid

            total_cogs = 0
            for item in items_data:
                item_cost_row = cursor.execute("SELECT purchase_price FROM items WHERE id = ?", (item['item_id'],)).fetchone()
                if item_cost_row is None: raise ValueError(f"Item with ID {item['item_id']} not found.")
                item_cost = item_cost_row['purchase_price'] or 0
                total_cogs += item_cost * item['quantity']

                cursor.execute("""
                    INSERT INTO sales_invoice_items (sales_invoice_id, item_id, quantity, selling_price, taxable_value, cgst_rate, sgst_rate, igst_rate, cgst_amount, sgst_amount, igst_amount, total_gst_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (sale_invoice_id, item['item_id'], item['quantity'], item['selling_price'], item.get('taxable_value', 0), item.get('cgst_rate', 0), item.get('sgst_rate', 0), item.get('igst_rate', 0), item.get('cgst_amount', 0), item.get('sgst_amount', 0), item.get('igst_amount', 0), item.get('total_gst_amount', 0)))

                if item.get('serial_ids'):
                    item_info = cursor.execute("SELECT default_warranty_months FROM items WHERE id = ?", (item['item_id'],)).fetchone()
                    warranty_months = item_info['default_warranty_months'] if item_info else 0
                    warranty_end_date = None
                    if warranty_months:
                        invoice_date = datetime.datetime.fromisoformat(invoice_data['invoice_date']).date()
                        warranty_end_date = (invoice_date + relativedelta(months=+warranty_months)).isoformat()
                    for sn_id in item['serial_ids']:
                        cursor.execute("UPDATE item_serial_numbers SET status = 'SOLD', sale_invoice_id = ?, warranty_end_date = ? WHERE id = ?", (sale_invoice_id, warranty_end_date, sn_id))

            rev_entries = [
                (accounts['Accounts Receivable'], invoice_data.get('total_amount', 0), None),
                (accounts['Sales Revenue'], None, invoice_data.get('taxable_amount', 0)),
                (accounts['GST Payable'], None, invoice_data.get('total_gst_amount', 0))
            ]
            create_gl_transaction(conn, f"Sale to cust ID {invoice_data['customer_id']}, Inv #{invoice_data['invoice_number']}", invoice_data['invoice_date'], rev_entries, 'SALE', sale_invoice_id)

            cogs_entries = [(accounts['Cost of Goods Sold'], total_cogs, None), (accounts['Inventory'], None, total_cogs)]
            create_gl_transaction(conn, f"COGS for Inv #{invoice_data['invoice_number']}", invoice_data['invoice_date'], cogs_entries, 'SALE_COGS', sale_invoice_id)

        return sale_invoice_id
    except (sqlite3.Error, ValueError) as e:
        print(f"Error creating sale invoice: {e}")
        return None

def record_customer_payment(customer_id, payment_date, amount, allocations):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            accounts = {name: id for id, name in cursor.execute("SELECT id, name FROM accounts WHERE name IN ('Cash', 'Accounts Receivable')").fetchall()}
            cursor.execute("INSERT INTO customer_payments (customer_id, payment_date, amount, notes) VALUES (?, ?, ?, ?)", (customer_id, payment_date, amount, ''))
            payment_id = cursor.lastrowid
            gl_entries = [(accounts['Cash'], amount, None), (accounts['Accounts Receivable'], None, amount)]
            create_gl_transaction(conn, f"Payment from customer ID {customer_id}", payment_date, gl_entries, 'CUST_PAYMENT', payment_id)
            for invoice_id, allocated_amount in allocations:
                cursor.execute("INSERT INTO customer_payment_allocations (payment_id, sales_invoice_id, amount) VALUES (?, ?, ?)", (payment_id, invoice_id, allocated_amount))
                cursor.execute("UPDATE sales_invoices SET amount_paid = amount_paid + ? WHERE id = ?", (allocated_amount, invoice_id))
                cursor.execute("UPDATE sales_invoices SET status = 'PAID' WHERE id = ? AND amount_paid >= total_amount", (invoice_id,))
        return payment_id
    except (sqlite3.Error, ValueError) as e: print(f"Error: {e}"); return None

def record_supplier_payment(supplier_id, payment_date, amount, allocations):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            accounts = {name: id for id, name in cursor.execute("SELECT id, name FROM accounts WHERE name IN ('Cash', 'Accounts Payable')").fetchall()}
            cursor.execute("INSERT INTO supplier_payments (supplier_id, payment_date, amount, notes) VALUES (?, ?, ?, ?)", (supplier_id, payment_date, amount, ''))
            payment_id = cursor.lastrowid
            gl_entries = [(accounts['Accounts Payable'], amount, None), (accounts['Cash'], None, amount)]
            create_gl_transaction(conn, f"Payment to supplier ID {supplier_id}", payment_date, gl_entries, 'SUPP_PAYMENT', payment_id)
            for invoice_id, allocated_amount in allocations:
                cursor.execute("INSERT INTO supplier_payment_allocations (payment_id, purchase_invoice_id, amount) VALUES (?, ?, ?)", (payment_id, invoice_id, allocated_amount))
                cursor.execute("UPDATE purchase_invoices SET amount_paid = amount_paid + ? WHERE id = ?", (allocated_amount, invoice_id))
                cursor.execute("UPDATE purchase_invoices SET status = 'PAID' WHERE id = ? AND amount_paid >= total_amount", (invoice_id,))
        return payment_id
    except (sqlite3.Error, ValueError) as e: print(f"Error: {e}"); return None

def mark_transactions_as_reconciled(transaction_ids, reconciliation_date):
    conn = get_db_connection()
    try:
        with conn:
            placeholders = ','.join('?' for _ in transaction_ids)
            conn.execute(f"UPDATE gl_transactions SET is_reconciled = TRUE, reconciliation_date = ? WHERE id IN ({placeholders})", [reconciliation_date] + transaction_ids)
        return True
    except sqlite3.Error as e: print(f"Error: {e}"); return False

# --- Reporting Functions ---
def get_gstr1_report_data(start_date, end_date):
    """
    Fetches and processes data for GSTR-1 report, separating B2B and B2C sales.
    """
    conn = get_db_connection()

    # B2B sales are those to customers WITH a GSTIN.
    b2b_query = """
    SELECT
        c.gstin as customer_gstin,
        si.invoice_number,
        si.invoice_date,
        si.total_amount,
        si.taxable_amount,
        si.cgst_amount,
        si.sgst_amount,
        si.igst_amount,
        c.state as place_of_supply
    FROM sales_invoices si
    JOIN customers c ON si.customer_id = c.id
    WHERE si.invoice_date BETWEEN ? AND ?
      AND c.gstin IS NOT NULL AND c.gstin != ''
    ORDER BY si.invoice_date;
    """

    # B2C sales are those to customers WITHOUT a GSTIN.
    # For GSTR-1, B2C sales are often summarized by Place of Supply (State) and Rate.
    b2c_summary_query = """
    SELECT
        c.state as place_of_supply,
        sii.cgst_rate + sii.sgst_rate + sii.igst_rate as total_rate,
        SUM(sii.taxable_value) as total_taxable_value,
        SUM(sii.cgst_amount) as total_cgst,
        SUM(sii.sgst_amount) as total_sgst,
        SUM(sii.igst_amount) as total_igst
    FROM sales_invoices si
    JOIN sales_invoice_items sii ON si.id = sii.sales_invoice_id
    JOIN customers c ON si.customer_id = c.id
    WHERE si.invoice_date BETWEEN ? AND ?
      AND (c.gstin IS NULL OR c.gstin = '')
    GROUP BY c.state, total_rate
    ORDER BY c.state;
    """

    b2b_invoices = conn.execute(b2b_query, (start_date, end_date)).fetchall()
    b2c_summary = conn.execute(b2c_summary_query, (start_date, end_date)).fetchall()

    conn.close()

    return {
        "b2b": [dict(row) for row in b2b_invoices],
        "b2c_summary": [dict(row) for row in b2c_summary]
    }

def get_gstr3b_report_data(start_date, end_date):
    """
    Fetches and processes summarized data for GSTR-3B report.
    """
    conn = get_db_connection()

    # 3.1: Outward Supplies (Sales)
    outward_supplies_query = """
    SELECT
        SUM(taxable_amount) as total_taxable,
        SUM(igst_amount) as total_igst,
        SUM(cgst_amount) as total_cgst,
        SUM(sgst_amount) as total_sgst
    FROM sales_invoices
    WHERE invoice_date BETWEEN ? AND ?;
    """

    # 4: Eligible ITC (Purchases)
    itc_query = """
    SELECT
        SUM(taxable_amount) as total_taxable,
        SUM(igst_amount) as total_igst,
        SUM(cgst_amount) as total_cgst,
        SUM(sgst_amount) as total_sgst
    FROM purchase_invoices
    WHERE invoice_date BETWEEN ? AND ?;
    """

    outward_data = conn.execute(outward_supplies_query, (start_date, end_date)).fetchone()
    itc_data = conn.execute(itc_query, (start_date, end_date)).fetchone()

    conn.close()

    return {
        "outward_supplies": dict(outward_data) if outward_data else {},
        "itc_details": dict(itc_data) if itc_data else {}
    }

def get_profit_and_loss_data(start_date, end_date):
    conn = get_db_connection()
    query = "SELECT a.type, a.name, IFNULL(SUM(ge.debit), 0) as total_debits, IFNULL(SUM(ge.credit), 0) as total_credits FROM gl_entries ge JOIN gl_transactions gt ON ge.transaction_id = gt.id JOIN accounts a ON ge.account_id = a.id WHERE a.type IN ('Revenue', 'Expense') AND gt.date BETWEEN ? AND ? GROUP BY a.id"
    results = conn.execute(query, (start_date, end_date)).fetchall()
    conn.close()
    return results

def get_balance_sheet_data(as_of_date):
    conn = get_db_connection()
    query = "SELECT a.type, a.name, IFNULL(SUM(ge.debit), 0) as total_debits, IFNULL(SUM(ge.credit), 0) as total_credits FROM gl_entries ge JOIN gl_transactions gt ON ge.transaction_id = gt.id JOIN accounts a ON ge.account_id = a.id WHERE a.type IN ('Asset', 'Liability', 'Equity') AND gt.date <= ? GROUP BY a.id"
    results = conn.execute(query, (as_of_date,)).fetchall()
    conn.close()
    return results

def get_expiring_warranties(days_ahead=30):
    conn = get_db_connection()
    today = datetime.date.today()
    future_date = today + datetime.timedelta(days=days_ahead)
    query = "SELECT i.name as item_name, sn.serial_number, sn.warranty_end_date, c.name as customer_name, si.invoice_number FROM item_serial_numbers sn JOIN items i ON sn.item_id = i.id JOIN sales_invoices si ON sn.sale_invoice_id = si.id JOIN customers c ON si.customer_id = c.id WHERE sn.status = 'SOLD' AND sn.warranty_end_date BETWEEN ? AND ? ORDER BY sn.warranty_end_date"
    results = conn.execute(query, (today.isoformat(), future_date.isoformat())).fetchall()
    conn.close()
    return results

def get_low_stock_report():
    conn = get_db_connection()
    query = "SELECT i.name, i.minimum_stock_level, COUNT(sn.id) as current_stock FROM items i LEFT JOIN item_serial_numbers sn ON i.id = sn.item_id AND sn.status = 'IN_STOCK' WHERE i.is_serialized = TRUE GROUP BY i.id HAVING COUNT(sn.id) < i.minimum_stock_level"
    results = conn.execute(query).fetchall()
    conn.close()
    return results

def get_category_stock_report():
    conn = get_db_connection()
    query = "SELECT i.category, COUNT(sn.id) as stock_count FROM items i JOIN item_serial_numbers sn ON i.id = sn.item_id WHERE sn.status = 'IN_STOCK' GROUP BY i.category"
    results = conn.execute(query).fetchall()
    conn.close()
    return results

# --- Service & Job Sheet Functions ---
def add_amc(customer_id, start_date, end_date, value):
    conn = get_db_connection()
    try: conn.execute("INSERT INTO amcs (customer_id, start_date, end_date, value) VALUES (?, ?, ?, ?)", (customer_id, start_date, end_date, value)); conn.commit(); return True
    except: return False
    finally: conn.close()

def get_all_amcs():
    conn = get_db_connection()
    amcs = conn.execute("SELECT a.*, c.name as customer_name FROM amcs a JOIN customers c ON a.customer_id = c.id ORDER BY a.end_date").fetchall()
    conn.close()
    return amcs

def add_amc_service_call(amc_id, service_date, details, solution):
    conn = get_db_connection()
    try: conn.execute("INSERT INTO amc_service_calls (amc_id, service_date, details, solution) VALUES (?, ?, ?, ?)", (amc_id, service_date, details, solution)); conn.commit(); return True
    except: return False
    finally: conn.close()

def get_service_calls_for_amc(amc_id):
    conn = get_db_connection()
    calls = conn.execute("SELECT * FROM amc_service_calls WHERE amc_id = ? ORDER BY service_date DESC", (amc_id,)).fetchall()
    conn.close()
    return calls

def get_expiring_amcs(days_ahead=30):
    conn = get_db_connection()
    today = datetime.date.today()
    future_date = today + datetime.timedelta(days=days_ahead)
    query = "SELECT a.*, c.name as customer_name FROM amcs a JOIN customers c ON a.customer_id = c.id WHERE a.end_date BETWEEN ? AND ? ORDER BY a.end_date"
    results = conn.execute(query, (today.isoformat(), future_date.isoformat())).fetchall()
    conn.close()
    return results

def add_job_sheet(data, accessories):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO job_sheets (customer_id, received_date, product_name, product_serial, reported_problem, status, estimated_cost, estimated_timeline, assigned_to) VALUES (:customer_id, :received_date, :product_name, :product_serial, :reported_problem, 'Received', :estimated_cost, :estimated_timeline, :assigned_to)", data)
            job_sheet_id = cursor.lastrowid
            if accessories:
                acc_data = [(job_sheet_id, name) for name in accessories]
                cursor.executemany("INSERT INTO job_sheet_accessories (job_sheet_id, name) VALUES (?, ?)", acc_data)
        return job_sheet_id
    except (sqlite3.Error, ValueError) as e: print(f"Error: {e}"); return None

def get_all_job_sheets():
    conn = get_db_connection()
    sheets = conn.execute("SELECT js.*, c.name as customer_name FROM job_sheets js JOIN customers c ON js.customer_id = c.id ORDER BY js.received_date DESC").fetchall()
    conn.close()
    return sheets

def get_job_sheet_details(job_sheet_id):
    conn = get_db_connection()
    sheet = conn.execute("SELECT js.*, c.name as customer_name FROM job_sheets js JOIN customers c ON js.customer_id = c.id WHERE js.id = ?", (job_sheet_id,)).fetchone()
    accessories = conn.execute("SELECT name FROM job_sheet_accessories WHERE job_sheet_id = ?", (job_sheet_id,)).fetchall()
    conn.close()
    return sheet, accessories

def update_job_sheet_status(job_sheet_id, status):
    conn = get_db_connection()
    try: conn.execute("UPDATE job_sheets SET status = ? WHERE id = ?", (status, job_sheet_id)); conn.commit(); return True
    except: return False
    finally: conn.close()

def create_quotation(data, items):
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO quotations (customer_id, quote_date, expiry_date, total_amount, status) VALUES (:customer_id, :quote_date, :expiry_date, :total_amount, 'DRAFT')", data)
            quote_id = cursor.lastrowid
            for item in items:
                cursor.execute("INSERT INTO quotation_items (quotation_id, item_id, quantity, selling_price) VALUES (?, ?, ?, ?)", (quote_id, item['item_id'], item['quantity'], item['selling_price']))
        return quote_id
    except (sqlite3.Error, ValueError) as e:
        print(f"Error: {e}"); return None

def get_all_quotations():
    conn = get_db_connection()
    quotes = conn.execute("SELECT q.*, c.name as customer_name FROM quotations q JOIN customers c ON q.customer_id = c.id ORDER BY q.quote_date DESC").fetchall()
    conn.close()
    return quotes

def get_quotation_details(quotation_id):
    conn = get_db_connection()
    quote = conn.execute("SELECT q.*, c.name as customer_name FROM quotations q JOIN customers c ON q.customer_id = c.id WHERE q.id = ?", (quotation_id,)).fetchone()
    # Also fetch gst_rate for conversion logic
    items_query = """
    SELECT qi.*, i.name as item_name, g.rate as gst_rate
    FROM quotation_items qi
    JOIN items i ON qi.item_id = i.id
    LEFT JOIN gst_slabs g ON i.gst_slab_id = g.id
    WHERE qi.quotation_id = ?
    """
    items = conn.execute(items_query, (quotation_id,)).fetchall()
    conn.close()
    return quote, items

def convert_quotation_to_sale(quotation_id, invoice_date):
    # This function needs a major overhaul to support the new GST structure.
    # For now, it's a placeholder, as the logic for tax calculation is not yet in place.
    # A real implementation would require calculating CGST, SGST, IGST based on company and customer state.
    print("WARNING: convert_quotation_to_sale is a placeholder and does not correctly calculate GST.")
    return None


# --- Import Functions ---
def import_customers_from_data(customers_data):
    """Imports or updates customers from a list of dictionaries."""
    conn = get_db_connection()
    updated_count, inserted_count = 0, 0
    try:
        with conn:
            for cust_dict in customers_data:
                existing = conn.execute("SELECT id FROM customers WHERE name = ?", (cust_dict['name'],)).fetchone()
                if existing:
                    conn.execute("UPDATE customers SET gstin=?, address=?, phone=?, email=?, state=? WHERE id=?",
                                 (cust_dict.get('gstin', ''), cust_dict.get('address', ''), cust_dict.get('phone', ''),
                                  cust_dict.get('email', ''), cust_dict.get('state', ''), existing['id']))
                    updated_count += 1
                else:
                    conn.execute("INSERT INTO customers (name, gstin, address, phone, email, state) VALUES (?, ?, ?, ?, ?, ?)",
                                 (cust_dict['name'], cust_dict.get('gstin', ''), cust_dict.get('address', ''),
                                  cust_dict.get('phone', ''), cust_dict.get('email', ''), cust_dict.get('state', '')))
                    inserted_count += 1
        return True, inserted_count, updated_count, None
    except sqlite3.Error as e:
        return False, 0, 0, str(e)

def import_purchases_from_data(invoices_data):
    """
    Imports a list of purchase invoices from validated data.
    NOTE: This is a simplified import that assumes all taxes are IGST for now.
    A full implementation would require state checking and CGST/SGST logic.
    """
    conn = get_db_connection()
    imported_count = 0
    try:
        with conn:
            all_suppliers = {s['name']: s['id'] for s in get_all_suppliers()}
            all_items = get_all_items()
            all_items_map = {i['name']: i for i in all_items}

            for inv in invoices_data:
                header = inv['data']['header']

                items_data_for_creation = []
                total_taxable_value = 0
                total_gst = 0

                for item_line in inv['data']['items']:
                    item_data = item_line['data']
                    item_info = all_items_map.get(item_data['item_name'])
                    if not item_info: continue

                    price = float(item_data['purchase_price'])
                    qty = float(item_data['quantity'])
                    taxable_value = price * qty
                    gst_rate = item_info.get('gst_rate', 0) # Assumes gst_rate is on the item for simplicity
                    gst_amount = taxable_value * (gst_rate / 100.0)

                    items_data_for_creation.append({
                        "item_id": item_info['id'], "quantity": qty, "purchase_price": price,
                        "taxable_value": taxable_value, "igst_rate": gst_rate, "igst_amount": gst_amount,
                        "total_gst_amount": gst_amount,
                        "serial_numbers": item_data.get('serial_numbers', []), "godown_id": 1
                    })
                    total_taxable_value += taxable_value
                    total_gst += gst_amount

                invoice_data = {
                    "supplier_id": all_suppliers[header['supplier_name']],
                    "invoice_number": header['invoice_number'], "invoice_date": header['invoice_date'],
                    "notes": header.get('notes', ''), "taxable_amount": total_taxable_value,
                    "igst_amount": total_gst, "cgst_amount": 0, "sgst_amount": 0,
                    "total_gst_amount": total_gst, "total_amount": total_taxable_value + total_gst
                }

                create_purchase_invoice_transaction(invoice_data, items_data_for_creation, conn_override=conn)
                imported_count += 1

        return True, imported_count, None
    except Exception as e:
        print(f"Error during purchase import: {e}")
        return False, 0, str(e)

def import_suppliers_from_data(suppliers_data):
    """Imports or updates suppliers from a list of dictionaries."""
    conn = get_db_connection()
    updated_count, inserted_count = 0, 0
    try:
        with conn:
            for supp_dict in suppliers_data:
                existing = conn.execute("SELECT id FROM suppliers WHERE name = ?", (supp_dict['name'],)).fetchone()
                if existing:
                    conn.execute("UPDATE suppliers SET gstin=?, address=?, phone=?, email=? WHERE id=?",
                                 (supp_dict.get('gstin', ''), supp_dict.get('address', ''),
                                  supp_dict.get('phone', ''), supp_dict.get('email', ''), existing['id']))
                    updated_count += 1
                else:
                    conn.execute("INSERT INTO suppliers (name, gstin, address, phone, email) VALUES (?, ?, ?, ?, ?)",
                                 (supp_dict['name'], supp_dict.get('gstin', ''), supp_dict.get('address', ''),
                                  supp_dict.get('phone', ''), supp_dict.get('email', '')))
                    inserted_count += 1
        return True, inserted_count, updated_count, None
    except sqlite3.Error as e:
        return False, 0, 0, str(e)

def import_items_from_data(items_data):
    """
    Imports or updates a list of items into the database within a single transaction.
    `items_data` is a list of dictionaries, each representing an item.
    """
    conn = get_db_connection()
    updated_count = 0
    inserted_count = 0

    try:
        with conn:
            for item_dict in items_data:
                existing_item = conn.execute("SELECT id FROM items WHERE name = ?", (item_dict['name'],)).fetchone()

                # Prepare data tuple for insertion/update
                data_tuple = (
                    item_dict.get('purchase_price', 0), item_dict.get('selling_price', 0),
                    item_dict.get('default_warranty_months', 0), item_dict.get('minimum_stock_level', 0),
                    item_dict.get('category', ''), item_dict.get('unit_id'),
                    item_dict.get('hsn_code_id'), item_dict.get('gst_slab_id'),
                    item_dict.get('is_serialized', False)
                )

                if existing_item:
                    # UPDATE existing item
                    conn.execute("""
                        UPDATE items SET purchase_price=?, selling_price=?,
                        default_warranty_months=?, minimum_stock_level=?, category=?, unit_id=?,
                        hsn_code_id=?, gst_slab_id=?, is_serialized=?
                        WHERE id=?
                    """, data_tuple + (existing_item['id'],))
                    updated_count += 1
                else:
                    # INSERT new item
                    conn.execute("""
                        INSERT INTO items (name, purchase_price, selling_price,
                        default_warranty_months, minimum_stock_level, category, unit_id,
                        hsn_code_id, gst_slab_id, is_serialized)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (item_dict['name'],) + data_tuple)
                    inserted_count += 1
        return True, inserted_count, updated_count, None
    except sqlite3.Error as e:
        print(f"Database error during bulk import: {e}")
        return False, 0, 0, str(e)

# --- Export Functions ---
def get_items_for_export():
    """Gets all items with their related names for CSV/PDF export."""
    conn = get_db_connection()
    query = """
    SELECT
        i.id, i.name, h.hsn_code, u.name as unit, i.category, i.purchase_price,
        i.selling_price, g.rate as gst_rate, i.default_warranty_months, i.minimum_stock_level
    FROM items i
    LEFT JOIN units u ON i.unit_id = u.id
    LEFT JOIN hsn_codes h ON i.hsn_code_id = h.id
    LEFT JOIN gst_slabs g ON i.gst_slab_id = g.id
    ORDER BY i.id
    """
    items = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in items]

def get_customers_for_export():
    """Gets all customers for CSV/PDF export."""
    conn = get_db_connection()
    customers = conn.execute("SELECT id, name, gstin, address, phone, email, state FROM customers ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in customers]

def get_suppliers_for_export():
    """Gets all suppliers for CSV/PDF export."""
    conn = get_db_connection()
    suppliers = conn.execute("SELECT id, name, gstin, address, phone, email FROM suppliers ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in suppliers]

def get_sales_invoices_for_export():
    """Gets all sales invoices with customer names for CSV/PDF export."""
    conn = get_db_connection()
    query = """
    SELECT
        si.id, si.invoice_number, si.invoice_date, c.name as customer_name,
        si.total_amount, si.gst_amount, si.status, si.amount_paid
    FROM sales_invoices si
    JOIN customers c ON si.customer_id = c.id
    ORDER BY si.id
    """
    invoices = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in invoices]

def get_purchase_invoices_for_export():
    """Gets all purchase invoices with supplier names for CSV/PDF export."""
    conn = get_db_connection()
    query = """
    SELECT
        pi.id, pi.invoice_number, pi.invoice_date, s.name as supplier_name,
        pi.total_amount, pi.gst_amount, pi.status, pi.amount_paid
    FROM purchase_invoices pi
    JOIN suppliers s ON pi.supplier_id = s.id
    ORDER BY pi.id
    """
    invoices = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in invoices]


# --- Transaction Viewer Functions ---
def get_sales_invoice_details(invoice_id):
    """Fetches full details for a single sales invoice, including line items."""
    conn = get_db_connection()

    invoice_query = "SELECT si.*, c.name as customer_name FROM sales_invoices si JOIN customers c ON si.customer_id = c.id WHERE si.id = ?"
    invoice = conn.execute(invoice_query, (invoice_id,)).fetchone()

    if not invoice:
        conn.close()
        return None, []

    items_query = """
    SELECT sii.*, i.name as item_name, i.hsn_code
    FROM sales_invoice_items sii
    JOIN items i ON sii.item_id = i.id
    WHERE sii.sales_invoice_id = ?
    """
    items = conn.execute(items_query, (invoice_id,)).fetchall()

    conn.close()
    return dict(invoice), [dict(item) for item in items]

def get_all_transactions(filters={}):
    """
    Fetches a unified list of all transactions based on a set of filters.
    """
    conn = get_db_connection()

    # Each subquery must select the same set of columns, aliased to be consistent
    sales_q = "SELECT si.id, si.invoice_date as date, 'Sales Invoice' as type, c.name as party_name, si.invoice_number as doc_number, si.total_amount, 'Customer' as party_type, si.customer_id as party_id FROM sales_invoices si JOIN customers c ON si.customer_id = c.id"
    purch_q = "SELECT pi.id, pi.invoice_date as date, 'Purchase Invoice' as type, s.name as party_name, pi.invoice_number as doc_number, pi.total_amount, 'Supplier' as party_type, pi.supplier_id as party_id FROM purchase_invoices pi JOIN suppliers s ON pi.supplier_id = s.id"
    cust_pay_q = "SELECT cp.id, cp.payment_date as date, 'Payment Received' as type, c.name as party_name, 'Payment #' || cp.id as doc_number, cp.amount as total_amount, 'Customer' as party_type, cp.customer_id as party_id FROM customer_payments cp JOIN customers c ON cp.customer_id = c.id"
    supp_pay_q = "SELECT sp.id, sp.payment_date as date, 'Payment Made' as type, s.name as party_name, 'Payment #' || sp.id as doc_number, sp.amount as total_amount, 'Supplier' as party_type, sp.supplier_id as party_id FROM supplier_payments sp JOIN suppliers s ON sp.supplier_id = s.id"

    queries = []
    trans_type = filters.get('transaction_type')
    if not trans_type or trans_type == 'All Transactions':
        queries.extend([sales_q, purch_q, cust_pay_q, supp_pay_q])
    elif trans_type == 'Sales Invoices': queries.append(sales_q)
    elif trans_type == 'Purchase Invoices': queries.append(purch_q)
    elif trans_type == 'Payments Received': queries.append(cust_pay_q)
    elif trans_type == 'Payments Made': queries.append(supp_pay_q)

    if not queries: return [] # Return empty if no valid type is selected

    base_query = " UNION ALL ".join(queries)

    where_clauses = []
    params = {}

    if filters.get('start_date'):
        where_clauses.append("date >= :start_date")
        params['start_date'] = filters['start_date']
    if filters.get('end_date'):
        where_clauses.append("date <= :end_date")
        params['end_date'] = filters['end_date']
    if filters.get('party_id') and filters.get('party_type'):
        where_clauses.append("party_id = :party_id AND party_type = :party_type")
        params['party_id'] = filters['party_id']
        params['party_type'] = filters['party_type']
    if filters.get('amount_min'):
        where_clauses.append("total_amount >= :amount_min")
        params['amount_min'] = filters['amount_min']
    if filters.get('amount_max'):
        where_clauses.append("total_amount <= :amount_max")
        params['amount_max'] = filters['amount_max']

    if where_clauses:
        final_query = f"SELECT * FROM ({base_query}) WHERE {' AND '.join(where_clauses)} ORDER BY date DESC"
    else:
        final_query = f"SELECT * FROM ({base_query}) ORDER BY date DESC"

    transactions = conn.execute(final_query, params).fetchall()
    conn.close()
    return transactions


def universal_search(search_term):
    if not search_term:
        return []
    conn = get_db_connection()
    term = f"%{search_term.lower()}%"
    all_results = []

    try:
        # Customers by name, phone, email, gstin
        customers = conn.execute("SELECT id, name, phone, email, gstin FROM customers WHERE lower(name) LIKE ? OR lower(phone) LIKE ? OR lower(email) LIKE ? OR lower(gstin) LIKE ?", (term, term, term, term)).fetchall()
        for row in customers:
            all_results.append({'type': 'Customer', 'summary': f"{row['name']}", 'details': f"Phone: {row['phone']}, Email: {row['email']}", 'id': row['id']})

        # Suppliers by name, phone, email, gstin
        suppliers = conn.execute("SELECT id, name, phone, email, gstin FROM suppliers WHERE lower(name) LIKE ? OR lower(phone) LIKE ? OR lower(email) LIKE ? OR lower(gstin) LIKE ?", (term, term, term, term)).fetchall()
        for row in suppliers:
            all_results.append({'type': 'Supplier', 'summary': f"{row['name']}", 'details': f"Phone: {row['phone']}, Email: {row['email']}", 'id': row['id']})

        # Items by name, hsn_code
        items_query = """
        SELECT i.id, i.name, h.hsn_code
        FROM items i
        LEFT JOIN hsn_codes h ON i.hsn_code_id = h.id
        WHERE lower(i.name) LIKE ? OR lower(h.hsn_code) LIKE ?
        """
        items = conn.execute(items_query, (term, term)).fetchall()
        for row in items:
            all_results.append({'type': 'Item', 'summary': f"{row['name']}", 'details': f"HSN: {row['hsn_code']}", 'id': row['id']})

        # Serial Numbers
        serials = conn.execute("SELECT sn.id, sn.serial_number, i.name as item_name FROM item_serial_numbers sn JOIN items i ON sn.item_id = i.id WHERE lower(sn.serial_number) LIKE ?", (term,)).fetchall()
        for row in serials:
            all_results.append({'type': 'Serial Number', 'summary': f"{row['serial_number']}", 'details': f"Item: {row['item_name']}", 'id': row['id']})

        # Sales Invoices by invoice number
        sales_invoices = conn.execute("SELECT si.id, si.invoice_number, c.name as customer_name FROM sales_invoices si JOIN customers c ON si.customer_id = c.id WHERE lower(si.invoice_number) LIKE ?", (term,)).fetchall()
        for row in sales_invoices:
            all_results.append({'type': 'Sales Invoice', 'summary': f"{row['invoice_number']}", 'details': f"Customer: {row['customer_name']}", 'id': row['id']})

        # Purchase Invoices by invoice number
        purchase_invoices = conn.execute("SELECT pi.id, pi.invoice_number, s.name as supplier_name FROM purchase_invoices pi JOIN suppliers s ON pi.supplier_id = s.id WHERE lower(pi.invoice_number) LIKE ?", (term,)).fetchall()
        for row in purchase_invoices:
            all_results.append({'type': 'Purchase Invoice', 'summary': f"{row['invoice_number']}", 'details': f"Supplier: {row['supplier_name']}", 'id': row['id']})

        # Job Sheets by product name or serial
        job_sheets = conn.execute("SELECT js.id, js.product_name, js.product_serial, c.name as customer_name FROM job_sheets js JOIN customers c ON js.customer_id = c.id WHERE lower(js.product_name) LIKE ? OR lower(js.product_serial) LIKE ?", (term, term)).fetchall()
        for row in job_sheets:
            all_results.append({'type': 'Job Sheet', 'summary': f"Job for {row['product_name']} (S/N: {row['product_serial']})", 'details': f"Customer: {row['customer_name']}", 'id': row['id']})

    except sqlite3.Error as e:
        print(f"Database search error: {e}")
    finally:
        if conn:
            conn.close()

    return all_results

# --- Dashboard Functions ---
def get_monthly_sales_summary():
    """Gets monthly sales summary for the current month."""
    conn = get_db_connection()
    try:
        # Get current month's first and last day
        today = datetime.date.today()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)
        
        query = """
        SELECT
            COUNT(*) as count,
            IFNULL(SUM(total_amount), 0) as total,
            IFNULL(SUM(taxable_amount), 0) as taxable_total,
            IFNULL(SUM(total_gst_amount), 0) as gst_total
        FROM sales_invoices
        WHERE invoice_date BETWEEN ? AND ?
        """
        result = conn.execute(query, (first_day.isoformat(), last_day.isoformat())).fetchone()
        return dict(result) if result else {'count': 0, 'total': 0, 'taxable_total': 0, 'gst_total': 0}
    except sqlite3.Error as e:
        print(f"Error getting monthly sales summary: {e}")
        return {'count': 0, 'total': 0, 'taxable_total': 0, 'gst_total': 0}
    finally:
        conn.close()

def get_monthly_purchase_summary():
    """Gets monthly purchase summary for the current month."""
    conn = get_db_connection()
    try:
        # Get current month's first and last day
        today = datetime.date.today()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - datetime.timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - datetime.timedelta(days=1)
        
        query = """
        SELECT
            COUNT(*) as count,
            IFNULL(SUM(total_amount), 0) as total,
            IFNULL(SUM(taxable_amount), 0) as taxable_total,
            IFNULL(SUM(total_gst_amount), 0) as gst_total
        FROM purchase_invoices
        WHERE invoice_date BETWEEN ? AND ?
        """
        result = conn.execute(query, (first_day.isoformat(), last_day.isoformat())).fetchone()
        return dict(result) if result else {'count': 0, 'total': 0, 'taxable_total': 0, 'gst_total': 0}
    except sqlite3.Error as e:
        print(f"Error getting monthly purchase summary: {e}")
        return {'count': 0, 'total': 0, 'taxable_total': 0, 'gst_total': 0}
    finally:
        conn.close()

def get_overdue_receivables_summary():
    """Gets summary of overdue receivables (unpaid sales invoices)."""
    conn = get_db_connection()
    try:
        query = """
        SELECT
            COUNT(*) as count,
            IFNULL(SUM(total_amount - amount_paid), 0) as total
        FROM sales_invoices
        WHERE status != 'PAID' AND (total_amount - amount_paid) > 0
        """
        result = conn.execute(query).fetchone()
        return dict(result) if result else {'count': 0, 'total': 0}
    except sqlite3.Error as e:
        print(f"Error getting overdue receivables summary: {e}")
        return {'count': 0, 'total': 0}
    finally:
        conn.close()

def get_recent_activities(limit=10):
    """Gets recent business activities for dashboard display."""
    conn = get_db_connection()
    try:
        # Union query to get recent activities from different tables
        query = """
        SELECT * FROM (
            SELECT
                invoice_date as date,
                'sale' as type,
                'Created invoice ' || invoice_number || ' for customer' as description,
                id
            FROM sales_invoices
            UNION ALL
            SELECT
                invoice_date as date,
                'purchase' as type,
                'Recorded purchase ' || invoice_number || ' from supplier' as description,
                id
            FROM purchase_invoices
            UNION ALL
            SELECT
                payment_date as date,
                'payment' as type,
                'Received payment ₹' || CAST(amount as TEXT) || ' from customer' as description,
                id
            FROM customer_payments
            UNION ALL
            SELECT
                payment_date as date,
                'payment' as type,
                'Made payment ₹' || CAST(amount as TEXT) || ' to supplier' as description,
                id
            FROM supplier_payments
        )
        ORDER BY date DESC
        LIMIT ?
        """
        results = conn.execute(query, (limit,)).fetchall()
        
        activities = []
        for row in results:
            # Calculate time ago (simplified)
            activity_date = datetime.datetime.fromisoformat(row['date']).date()
            today = datetime.date.today()
            days_ago = (today - activity_date).days
            
            if days_ago == 0:
                time_str = "Today"
            elif days_ago == 1:
                time_str = "1 day ago"
            else:
                time_str = f"{days_ago} days ago"
            
            activities.append({
                'type': row['type'],
                'description': row['description'],
                'time': time_str
            })
        
        return activities
    except sqlite3.Error as e:
        print(f"Error getting recent activities: {e}")
        return []
    finally:
        conn.close()
