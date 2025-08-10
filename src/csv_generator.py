import csv

def generate_purchases_template(filename):
    """Creates a sample CSV template file for importing purchase invoices."""
    headers = [
        "invoice_number", "supplier_name", "invoice_date", "notes",
        "item_name", "quantity", "purchase_price", "gst_rate",
        "serial_numbers" # Comma-separated for serialized items
    ]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            # Add a sample row to explain the format
            writer.writerow(["PUR-101", "Supplier A", "2023-10-26", "First purchase", "Item X", "10", "99.50", "18", ""])
            writer.writerow(["PUR-101", "Supplier A", "2023-10-26", "First purchase", "Item Y (Serialized)", "2", "500.00", "18", "SN001,SN002"])
            writer.writerow(["PUR-102", "Supplier B", "2023-10-27", "", "Item Z", "5", "25.00", "5", ""])
        return True, None
    except (IOError, csv.Error) as e:
        print(f"Error generating template: {e}")
        return False, str(e)

def generate_suppliers_template(filename):
    """Creates a sample CSV template file for importing suppliers."""
    headers = ["name", "gstin", "address", "phone", "email"]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
        return True, None
    except (IOError, csv.Error) as e:
        print(f"Error generating template: {e}")
        return False, str(e)

def generate_customers_template(filename):
    """Creates a sample CSV template file for importing customers."""
    headers = ["name", "gstin", "address", "phone", "email", "state"]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
        return True, None
    except (IOError, csv.Error) as e:
        print(f"Error generating template: {e}")
        return False, str(e)

def generate_items_template(filename):
    """Creates a sample CSV template file for importing items."""
    headers = [
        "name", "hsn_code", "gst_rate", "purchase_price", "selling_price",
        "default_warranty_months", "minimum_stock_level", "category",
        "unit_name", "is_serialized"
    ]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
        return True, None
    except (IOError, csv.Error) as e:
        print(f"Error generating template: {e}")
        return False, str(e)

def export_to_csv(data, filename):
    """
    Exports a list of dictionaries to a CSV file.
    The keys of the first dictionary are used as headers.
    """
    if not data:
        return False, "No data to export."

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return True, None
    except (IOError, csv.Error) as e:
        print(f"Error exporting to CSV: {e}")
        return False, str(e)
