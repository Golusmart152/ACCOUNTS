from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import datetime
import db_manager
from reportlab.lib.utils import ImageReader

# A simple text wrapper
def wrap_text(text, line_length):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 > line_length:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
    lines.append(current_line.strip())
    return [line for line in lines if line]

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def export_to_pdf(data, filename, title):
    """
    Exports a list of dictionaries to a PDF file with a title and a table.
    """
    if not data:
        return False, "No data to export."

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles['h1']))

        # Convert list of dicts to list of lists for the table
        headers = list(data[0].keys())
        table_data = [headers] + [[str(item.get(h, '')) for h in headers] for item in data]

        # Create and style the table
        t = Table(table_data, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        t.setStyle(style)

        elements.append(t)
        doc.build(elements)

        return True, None
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        return False, str(e)

def generate_account_statement_pdf(filename, party, start_date, end_date, opening_balance, transactions):
    """Generates a PDF for a party's account statement."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = f"Statement of Account for {party['name']}"
    elements.append(Paragraph(title, styles['h1']))

    # Date Range
    date_range = f"For the period: {start_date} to {end_date}"
    elements.append(Paragraph(date_range, styles['h3']))

    # Summary
    summary_text = f"Opening Balance: {opening_balance:,.2f}"
    elements.append(Paragraph(summary_text, styles['Normal']))

    # Table Data
    table_data = [["Date", "Particulars", "Doc #", "Debit", "Credit", "Balance"]]
    balance = opening_balance

    for trans in transactions:
        debit = trans['debit'] or 0.0
        credit = trans['credit'] or 0.0
        balance += (debit - credit)
        table_data.append([
            trans['date'], trans['type'], trans['document_number'],
            f"{debit:,.2f}", f"{credit:,.2f}", f"{balance:,.2f}"
        ])

    # Closing Balance Row
    table_data.append(["", "", "Closing Balance", "", "", f"{balance:,.2f}"])

    # Create and style the table
    t = Table(table_data, repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (3,1), (-1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    t.setStyle(style)

    elements.append(t)
    doc.build(elements)
    return True, None

def generate_job_sheet_pdf(filename, data):
    """
    Generates a PDF for a job sheet, including company details from settings.
    `data` is a dictionary containing all the necessary job sheet information.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    settings = db_manager.get_all_settings()

    # --- Page Header ---
    # Draw logo if it exists
    logo_path = settings.get("company_logo_path")
    if logo_path:
        try:
            # Using a fixed size for the logo for layout stability
            c.drawImage(logo_path, inch, height - 1.5*inch, width=1.5*inch, height=1*inch, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Could not draw logo image: {e}")

    # Company Details (right-aligned)
    company_name = settings.get("company_name", "Your Company")
    c.setFont("Helvetica-Bold", 18)
    c.drawRightString(width - inch, height - inch, company_name)

    c.setFont("Helvetica", 10)
    company_address = settings.get("company_address", "123 Business Rd, Suite 456, City")
    company_phone = settings.get("company_phone", "555-1234")
    company_email = settings.get("company_email", "contact@company.com")
    c.drawRightString(width - inch, height - 1.2*inch, company_address)
    c.drawRightString(width - inch, height - 1.4*inch, f"Phone: {company_phone} | Email: {company_email}")

    # --- Document Title ---
    c.setFont("Helvetica-Bold", 16)
    c.drawString(inch, height - 2.2*inch, "Service Job Sheet")
    c.setFont("Helvetica", 10)
    c.drawString(inch, height - 2.4*inch, f"Job Sheet #: {data['id']}")
    c.drawString(width - 2.5*inch, height - 2.4*inch, f"Date: {data['received_date']}")
    c.line(inch, height - 2.5*inch, width - inch, height - 2.5*inch)

    # --- Customer & Product Details ---
    y_pos = height - 2.8*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_pos, "Customer Information")
    c.setFont("Helvetica", 11)
    y_pos -= 0.25*inch
    c.drawString(inch, y_pos, f"Name: {data['customer_name']}")
    c.drawString(width/2, y_pos, f"Phone: {data.get('phone', 'N/A')}")

    y_pos -= 0.4*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_pos, "Product Information")
    y_pos -= 0.25*inch
    c.setFont("Helvetica", 11)
    c.drawString(inch, y_pos, f"Product: {data['product_name']}")
    c.drawString(width/2, y_pos, f"Serial #: {data['product_serial']}")

    # --- Problem & Accessories ---
    y_pos -= 0.4*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(inch, y_pos, "Reported Problem:")
    c.setFont("Helvetica", 10)
    problem_lines = wrap_text(data['reported_problem'], 90)
    for line in problem_lines:
        y_pos -= 0.2*inch
        c.drawString(inch + 0.1*inch, y_pos, line)

    y_pos -= 0.3*inch
    c.setFont("Helvetica-Bold", 11)
    c.drawString(inch, y_pos, "Accessories Submitted:")
    c.setFont("Helvetica", 10)
    acc_str = ", ".join(data['accessories']) if data['accessories'] else "None"
    acc_lines = wrap_text(acc_str, 90)
    for line in acc_lines:
        y_pos -= 0.2*inch
        c.drawString(inch + 0.1*inch, y_pos, line)

    # --- Estimates & Assignment ---
    y_pos -= 0.4*inch
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y_pos, "Service Estimates")
    c.setFont("Helvetica", 11)
    y_pos -= 0.25*inch
    c.drawString(inch, y_pos, f"Estimated Cost: Rs. {data.get('estimated_cost', 0):.2f}")
    c.drawString(width/2, y_pos, f"Estimated Timeline: {data.get('estimated_timeline', 'N/A')}")

    if data.get('assigned_to'):
        y_pos -= 0.25*inch
        c.drawString(inch, y_pos, f"Assigned To: {data['assigned_to']}")

    # --- Footer ---
    y_pos = 2.5 * inch
    c.line(inch, y_pos, width - inch, y_pos)
    y_pos -= 0.2*inch

    # Terms and Conditions
    c.setFont("Helvetica-Oblique", 8)
    terms = settings.get("doc_terms_conditions", "1. Device must be collected within 30 days. 2. We are not responsible for data loss.")
    terms_lines = wrap_text(terms, 120)
    for line in terms_lines:
        c.drawString(inch, y_pos, line)
        y_pos -= 0.15*inch

    # Bank Details
    y_pos -= 0.1*inch
    bank_name = settings.get("bank_account_name")
    if bank_name:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(inch, y_pos, "Bank Details for Payment:")
        y_pos -= 0.15*inch
        c.setFont("Helvetica", 9)
        bank_num = settings.get("bank_account_number", "")
        bank_ifsc = settings.get("bank_ifsc_code", "")
        c.drawString(inch, y_pos, f"Account: {bank_name}, Number: {bank_num}, IFSC: {bank_ifsc}")

    # Signature line
    y_pos = 1.2 * inch
    c.line(width - 3.5*inch, y_pos, width - inch, y_pos)
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    c.drawRightString(width - inch - 0.75*inch, y_pos, "Customer Signature")

    c.save()
    print(f"PDF generated: {filename}")
