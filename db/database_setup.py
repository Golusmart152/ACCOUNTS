import sqlite3

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to {db_file}, SQLite version: {sqlite3.sqlite_version}")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def setup_database(db_path="db/accounting.db"):
    """
    Sets up the database schema at the given path.
    Defaults to the main application database.
    """
    conn = create_connection(db_path)

    if conn is not None:
        conn.execute("PRAGMA foreign_keys = ON")

        # --- Base & Entity Tables ---
        create_table(conn, "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS gst_slabs (id INTEGER PRIMARY KEY, rate REAL NOT NULL UNIQUE, description TEXT);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS hsn_codes (id INTEGER PRIMARY KEY, hsn_code TEXT NOT NULL UNIQUE, description TEXT, gst_slab_id INTEGER, FOREIGN KEY(gst_slab_id) REFERENCES gst_slabs(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS units (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS compound_units (id INTEGER PRIMARY KEY, base_unit_id INTEGER NOT NULL, secondary_unit_id INTEGER NOT NULL, conversion_factor REAL NOT NULL, FOREIGN KEY(base_unit_id) REFERENCES units(id), FOREIGN KEY(secondary_unit_id) REFERENCES units(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS godowns (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, location TEXT);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, hsn_code_id INTEGER, gst_slab_id INTEGER, purchase_price REAL, selling_price REAL, default_warranty_months INTEGER, minimum_stock_level INTEGER, is_assembled_item BOOLEAN DEFAULT FALSE, is_serialized BOOLEAN DEFAULT FALSE, unit_id INTEGER, FOREIGN KEY(unit_id) REFERENCES units(id), FOREIGN KEY(gst_slab_id) REFERENCES gst_slabs(id), FOREIGN KEY(hsn_code_id) REFERENCES hsn_codes(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, gstin TEXT, address TEXT, phone TEXT, email TEXT, state TEXT);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, gstin TEXT, address TEXT, phone TEXT, email TEXT, state TEXT, billing_address TEXT, shipping_address TEXT, credit_limit REAL);")

        # --- Core Accounting Tables ---
        create_table(conn, "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, type TEXT NOT NULL, is_predefined BOOLEAN DEFAULT FALSE);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS gl_transactions (id INTEGER PRIMARY KEY, date TEXT NOT NULL, description TEXT NOT NULL, source_doc_type TEXT, source_doc_id INTEGER);")
        create_table(conn, "CREATE TABLE IF NOT EXISTS gl_entries (id INTEGER PRIMARY KEY, transaction_id INTEGER NOT NULL, account_id INTEGER NOT NULL, debit REAL, credit REAL, FOREIGN KEY(transaction_id) REFERENCES gl_transactions(id), FOREIGN KEY(account_id) REFERENCES accounts(id));")

        # --- Transaction Tables (Dropping and recreating to add new columns) ---
        conn.execute("DROP TABLE IF EXISTS purchase_invoices;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS purchase_invoices (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL, invoice_number TEXT NOT NULL, invoice_date TEXT NOT NULL, total_amount REAL NOT NULL, taxable_amount REAL, cgst_amount REAL, sgst_amount REAL, igst_amount REAL, total_gst_amount REAL, notes TEXT, status TEXT DEFAULT 'UNPAID', amount_paid REAL DEFAULT 0.0, FOREIGN KEY (supplier_id) REFERENCES suppliers (id), UNIQUE (supplier_id, invoice_number));")
        conn.execute("DROP TABLE IF EXISTS sales_invoices;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS sales_invoices (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, invoice_number TEXT NOT NULL UNIQUE, invoice_date TEXT NOT NULL, total_amount REAL NOT NULL, taxable_amount REAL, cgst_amount REAL, sgst_amount REAL, igst_amount REAL, total_gst_amount REAL, notes TEXT, status TEXT DEFAULT 'UNPAID', amount_paid REAL DEFAULT 0.0, FOREIGN KEY (customer_id) REFERENCES customers (id));")

        conn.execute("DROP TABLE IF EXISTS purchase_invoice_items;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS purchase_invoice_items (id INTEGER PRIMARY KEY, purchase_invoice_id INTEGER NOT NULL, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, purchase_price REAL NOT NULL, taxable_value REAL, cgst_rate REAL, sgst_rate REAL, igst_rate REAL, cgst_amount REAL, sgst_amount REAL, igst_amount REAL, total_gst_amount REAL, FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices (id), FOREIGN KEY (item_id) REFERENCES items (id));")
        conn.execute("DROP TABLE IF EXISTS sales_invoice_items;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS sales_invoice_items (id INTEGER PRIMARY KEY, sales_invoice_id INTEGER NOT NULL, item_id INTEGER NOT NULL, quantity INTEGER NOT NULL, selling_price REAL NOT NULL, taxable_value REAL, cgst_rate REAL, sgst_rate REAL, igst_rate REAL, cgst_amount REAL, sgst_amount REAL, igst_amount REAL, total_gst_amount REAL, FOREIGN KEY (sales_invoice_id) REFERENCES sales_invoices (id), FOREIGN KEY (item_id) REFERENCES items (id));")

        # --- Payment & Linking Tables ---
        create_table(conn, "CREATE TABLE IF NOT EXISTS customer_payments (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, payment_date TEXT NOT NULL, amount REAL NOT NULL, notes TEXT, FOREIGN KEY(customer_id) REFERENCES customers(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS supplier_payments (id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL, payment_date TEXT NOT NULL, amount REAL NOT NULL, notes TEXT, FOREIGN KEY(supplier_id) REFERENCES suppliers(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS customer_payment_allocations (payment_id INTEGER NOT NULL, sales_invoice_id INTEGER NOT NULL, amount REAL NOT NULL, PRIMARY KEY (payment_id, sales_invoice_id), FOREIGN KEY(payment_id) REFERENCES customer_payments(id), FOREIGN KEY(sales_invoice_id) REFERENCES sales_invoices(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS supplier_payment_allocations (payment_id INTEGER NOT NULL, purchase_invoice_id INTEGER NOT NULL, amount REAL NOT NULL, PRIMARY KEY (payment_id, purchase_invoice_id), FOREIGN KEY(payment_id) REFERENCES supplier_payments(id), FOREIGN KEY(purchase_invoice_id) REFERENCES purchase_invoices(id));")

        # --- Inventory & Other Linking Tables ---
        conn.execute("DROP TABLE IF EXISTS item_serial_numbers;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS item_serial_numbers (id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL, serial_number TEXT NOT NULL UNIQUE, status TEXT NOT NULL, godown_id INTEGER NOT NULL, purchase_invoice_id INTEGER, sale_invoice_id INTEGER, warranty_end_date TEXT, FOREIGN KEY (item_id) REFERENCES items (id), FOREIGN KEY (godown_id) REFERENCES godowns (id), FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoices (id), FOREIGN KEY (sale_invoice_id) REFERENCES sales_invoices (id));")
        conn.execute("DROP TABLE IF EXISTS assemblies;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS assemblies (id INTEGER PRIMARY KEY, assembled_item_id INTEGER NOT NULL, new_serial_number_id INTEGER NOT NULL, total_cost REAL NOT NULL, assembly_date TEXT NOT NULL, FOREIGN KEY (assembled_item_id) REFERENCES items (id), FOREIGN KEY (new_serial_number_id) REFERENCES item_serial_numbers (id));")
        conn.execute("DROP TABLE IF EXISTS assembly_components;")
        create_table(conn, "CREATE TABLE IF NOT EXISTS assembly_components (id INTEGER PRIMARY KEY, assembly_id INTEGER NOT NULL, component_item_id INTEGER NOT NULL, used_serial_number_id INTEGER NOT NULL, FOREIGN KEY (assembly_id) REFERENCES assemblies (id), FOREIGN KEY (component_item_id) REFERENCES items (id), FOREIGN KEY (used_serial_number_id) REFERENCES item_serial_numbers (id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS item_batches (id INTEGER PRIMARY KEY, item_id INTEGER NOT NULL, batch_number TEXT NOT NULL, expiry_date TEXT, quantity INTEGER NOT NULL, godown_id INTEGER NOT NULL, FOREIGN KEY (item_id) REFERENCES items (id), FOREIGN KEY (godown_id) REFERENCES godowns (id));")

        # --- Service Tables ---
        create_table(conn, "CREATE TABLE IF NOT EXISTS amcs (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, value REAL NOT NULL, FOREIGN KEY(customer_id) REFERENCES customers(id));")
        create_table(conn, "CREATE TABLE IF NOT EXISTS amc_service_calls (id INTEGER PRIMARY KEY, amc_id INTEGER NOT NULL, service_date TEXT NOT NULL, details TEXT, solution TEXT, FOREIGN KEY(amc_id) REFERENCES amcs(id));")
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS job_sheets (
            id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, received_date TEXT NOT NULL, product_name TEXT, product_serial TEXT,
            reported_problem TEXT, status TEXT, estimated_cost REAL, estimated_timeline TEXT, assigned_to TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );""")
        create_table(conn, "CREATE TABLE IF NOT EXISTS job_sheet_accessories (id INTEGER PRIMARY KEY, job_sheet_id INTEGER NOT NULL, name TEXT NOT NULL, FOREIGN KEY(job_sheet_id) REFERENCES job_sheets(id));")

        # --- Pre-Sales Tables ---
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, quote_date TEXT NOT NULL, expiry_date TEXT,
            total_amount REAL NOT NULL, status TEXT DEFAULT 'DRAFT',
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        );""")
        create_table(conn, """
        CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY, quotation_id INTEGER NOT NULL, item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL, selling_price REAL NOT NULL,
            FOREIGN KEY(quotation_id) REFERENCES quotations(id), FOREIGN KEY(item_id) REFERENCES items(id)
        );""")

        # --- Schema Migrations / Alterations ---
        try:
            conn.execute("ALTER TABLE gl_transactions ADD COLUMN is_reconciled BOOLEAN DEFAULT FALSE;")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            conn.execute("ALTER TABLE gl_transactions ADD COLUMN reconciliation_date TEXT;")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            conn.execute("ALTER TABLE items ADD COLUMN category TEXT;")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            conn.execute("ALTER TABLE items ADD COLUMN unit_id INTEGER;")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            conn.execute("ALTER TABLE items ADD COLUMN hsn_code_id INTEGER;")
        except sqlite3.OperationalError:
            pass # Column already exists
        try:
            conn.execute("ALTER TABLE customers ADD COLUMN billing_address TEXT;")
            conn.execute("ALTER TABLE customers ADD COLUMN shipping_address TEXT;")
            conn.execute("ALTER TABLE customers ADD COLUMN credit_limit REAL;")
        except sqlite3.OperationalError:
            pass # Columns already exist

        # Pre-populate units
        try:
            cursor = conn.cursor()
            default_units = [('Pcs',), ('Nos',), ('Box',), ('Dozen',), ('Meter',), ('Kg',), ('Gram',), ('Liter',)]
            cursor.executemany("INSERT OR IGNORE INTO units (name) VALUES (?)", default_units)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Could not pre-populate units: {e}")

        # Pre-populate gst_slabs and default settings
        try:
            cursor = conn.cursor()
            default_slabs = [
                (0, 'Exempt'),
                (5, 'GST 5%'),
                (12, 'GST 12%'),
                (18, 'GST 18%'),
                (28, 'GST 28%')
            ]
            cursor.executemany("INSERT OR IGNORE INTO gst_slabs (rate, description) VALUES (?, ?)", default_slabs)

            # Set default company state
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('company_state', ''))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Could not pre-populate GST slabs or settings: {e}")

        print("Database tables created successfully.")
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    setup_database()
