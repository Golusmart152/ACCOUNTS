import csv
import db_manager
import datetime

def validate_customers_csv(file_path):
    """Reads a customers CSV, validates it, and returns data with status."""
    validated_data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                errors = []
                row = {k.strip(): v.strip() for k, v in row.items()}
                if not row.get('name'):
                    errors.append("'name' cannot be empty.")
                validated_data.append({'data': row, 'is_valid': not errors, 'errors': ", ".join(errors)})
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"
    return validated_data, None

from collections import defaultdict

def validate_purchases_csv(file_path):
    """Reads a purchase invoices CSV, validates it, and returns structured data."""
    invoices = defaultdict(lambda: {'items': [], 'errors': []})
    all_suppliers = {s['name']: s['id'] for s in db_manager.get_all_suppliers()}
    all_items = {i['name']: i for i in db_manager.get_all_items()}

    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                inv_num = row.get('invoice_number')
                if not inv_num:
                    # This row is invalid, but we can't group it. Skip or handle as a global error.
                    continue
                invoices[inv_num]['items'].append(row)

        validated_invoices = []
        for inv_num, inv_data in invoices.items():
            is_valid = True
            header_errors = []

            # Use data from the first item for header info
            header_row = inv_data['items'][0]
            supplier_name = header_row.get('supplier_name')
            if not supplier_name or supplier_name not in all_suppliers:
                is_valid = False
                header_errors.append(f"Supplier '{supplier_name}' not found.")

            try:
                datetime.datetime.strptime(header_row.get('invoice_date', ''), '%Y-%m-%d')
            except ValueError:
                is_valid = False
                header_errors.append("Invalid date format (must be YYYY-MM-DD).")

            validated_items = []
            for item_row in inv_data['items']:
                item_errors = []
                item_name = item_row.get('item_name')
                item_info = all_items.get(item_name)

                if not item_info:
                    item_errors.append(f"Item '{item_name}' not found.")
                else:
                    try:
                        qty = float(item_row.get('quantity', '0'))
                        price = float(item_row.get('purchase_price', '0'))

                        if item_info['is_serialized']:
                            serials = [s.strip() for s in item_row.get('serial_numbers', '').split(',') if s.strip()]
                            if len(serials) != int(qty):
                                item_errors.append("Number of serials must match quantity.")
                            item_row['serial_numbers'] = serials
                    except (ValueError, TypeError):
                        item_errors.append("Qty and Price must be valid numbers.")

                if item_errors:
                    is_valid = False
                validated_items.append({'data': item_row, 'errors': ", ".join(item_errors)})

            validated_invoices.append({
                'data': {'header': header_row, 'items': validated_items},
                'is_valid': is_valid,
                'errors': ", ".join(header_errors)
            })

    except Exception as e:
        return None, f"An unexpected error occurred: {e}"
    return validated_invoices, None


def validate_suppliers_csv(file_path):
    """Reads a suppliers CSV, validates it, and returns data with status."""
    validated_data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                errors = []
                row = {k.strip(): v.strip() for k, v in row.items()}
                if not row.get('name'):
                    errors.append("'name' cannot be empty.")
                validated_data.append({'data': row, 'is_valid': not errors, 'errors': ", ".join(errors)})
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"
    return validated_data, None

def validate_items_csv(file_path):
    """
    Reads an items CSV file, validates each row, and returns the parsed data
    with validation status.
    """
    validated_data = []
    all_units = {u['name']: u['id'] for u in db_manager.get_all_units()}

    try:
        with open(file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for i, row in enumerate(reader):
                errors = []
                # Clean up keys and values
                row = {k.strip(): v.strip() for k, v in row.items()}

                # 1. Validate Name
                name = row.get('name')
                if not name:
                    errors.append("'name' cannot be empty.")

                # 2. Validate Numeric Fields
                numeric_fields = {
                    'gst_rate': float, 'purchase_price': float, 'selling_price': float,
                    'default_warranty_months': int, 'minimum_stock_level': int
                }
                for field, type_converter in numeric_fields.items():
                    val = row.get(field)
                    if val:
                        try:
                            row[field] = type_converter(val)
                        except (ValueError, TypeError):
                            errors.append(f"'{field}' must be a valid number.")
                    else:
                        row[field] = 0 # Default to 0 if empty

                # 3. Validate Unit
                unit_name = row.get('unit_name')
                if not unit_name:
                    errors.append("'unit_name' is required.")
                elif unit_name not in all_units:
                    errors.append(f"Unit '{unit_name}' does not exist. Please add it first.")
                else:
                    row['unit_id'] = all_units[unit_name] # Add unit_id for importer

                # 4. Validate Boolean
                is_serialized_str = row.get('is_serialized', 'FALSE').upper()
                if is_serialized_str not in ['TRUE', 'FALSE', '1', '0']:
                    errors.append("'is_serialized' must be TRUE or FALSE.")
                row['is_serialized'] = is_serialized_str in ['TRUE', '1']

                # Final validation status
                validated_row = {
                    'data': row,
                    'is_valid': not errors,
                    'errors': ", ".join(errors)
                }
                validated_data.append(validated_row)

    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

    return validated_data, None
