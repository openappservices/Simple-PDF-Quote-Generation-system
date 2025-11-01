# app.py
from flask import Flask, request, send_file, render_template_string
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os
from datetime import datetime, timedelta

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Quotation Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
            font-weight: 600;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        .services-container {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .service-item {
            display: grid;
            grid-template-columns: 60px 1fr 80px 100px auto;
            gap: 10px;
            margin-bottom: 10px;
            align-items: end;
        }
        .service-item input[type="number"] {
            text-align: center;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-secondary {
            background: #28a745;
            color: white;
        }
        .btn-secondary:hover {
            background: #218838;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
            padding: 10px 15px;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .grid-3 {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #1976d2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 Quotation Generator</h1>
        
        <form method="POST" action="/" enctype="multipart/form-data">
            <div class="form-group">
                <label>Company Name *</label>
                <input type="text" name="company_name" required>
            </div>
            
            <div class="grid-3">
                <div class="form-group">
                    <label>Quotation Number *</label>
                    <input type="text" name="quotation_number" required placeholder="QT-2025-001">
                </div>
                
                <div class="form-group">
                    <label>Date *</label>
                    <input type="date" name="date" required>
                </div>
                
                <div class="form-group">
                    <label>Currency *</label>
                    <select name="currency" required>
                        <option value="USD ">Dollar ($)</option>
                        <option value="INR ">Indian Rupees (₹)</option>
                    </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>Generated By *</label>
                <input type="text" name="generated_by" required>
            </div>
            
            <div class="form-group">
                <label>Customer Name *</label>
                <input type="text" name="customer_name" required>
            </div>
            
            <div class="form-group">
                <label>Customer Contact (Email | Phone) *</label>
                <input type="text" name="customer_contact" required placeholder="email@example.com | +91-98765-43210">
            </div>
            
            <div class="services-container">
                <label style="margin-bottom: 15px;">Services *</label>
                <div class="info-box">
                    💡 Add services with serial number, description, quantity, and cost per unit
                </div>
                <div id="services">
                    <div class="service-item">
                        <input type="number" name="service_sl[]" placeholder="Sl No" min="1" value="1" required>
                        <input type="text" name="service_desc[]" placeholder="Service Description" required>
                        <input type="number" name="service_qty[]" placeholder="Qty" min="1" value="1" required>
                        <input type="number" name="service_cost[]" placeholder="Cost" step="0.01" required>
                        <button type="button" class="btn btn-danger" onclick="removeService(this)">✕</button>
                    </div>
                </div>
                <button type="button" class="btn btn-secondary" onclick="addService()">+ Add Service</button>
            </div>
            
            <div class="form-group">
                <label>Tax (GST %) - Optional</label>
                <input type="number" name="tax_rate" step="0.01" placeholder="0" value="0">
            </div>
            
            <div class="form-group">
                <label>Notes (Optional - Max 50 lines)</label>
                <textarea name="notes" rows="8" maxlength="5000" placeholder="Enter any additional notes, terms, or conditions..."></textarea>
            </div>
            
            <button type="submit" class="btn btn-primary">Generate Quotation PDF</button>
        </form>
    </div>
    
    <script>
        let serviceCount = 1;
        
        function addService() {
            serviceCount++;
            const servicesDiv = document.getElementById('services');
            const serviceItem = document.createElement('div');
            serviceItem.className = 'service-item';
            serviceItem.innerHTML = `
                <input type="number" name="service_sl[]" placeholder="Sl No" min="1" value="${serviceCount}" required>
                <input type="text" name="service_desc[]" placeholder="Service Description" required>
                <input type="number" name="service_qty[]" placeholder="Qty" min="1" value="1" required>
                <input type="number" name="service_cost[]" placeholder="Cost" step="0.01" required>
                <button type="button" class="btn btn-danger" onclick="removeService(this)">✕</button>
            `;
            servicesDiv.appendChild(serviceItem);
        }
        
        function removeService(button) {
            const servicesDiv = document.getElementById('services');
            if (servicesDiv.children.length > 1) {
                button.parentElement.remove();
            } else {
                alert('At least one service is required');
            }
        }
    </script>
</body>
</html>
"""

def create_quotation(company_name, quotation_number, date, generated_by,
                     customer_name, customer_contact, services, tax_rate=0, 
                     currency="USD", notes="", filename="quotation.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Currency symbol
    currency_symbol = "$" if currency == "USD" else "INR "
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )
    
    small_text_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_JUSTIFY
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=5
    )
    
    footer_small_style = ParagraphStyle(
        'FooterSmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(company_name, title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("QUOTATION", heading_style))
    
    # Calculate validity date (20 days from quote date)
    try:
        quote_date = datetime.strptime(date, "%Y-%m-%d")
        valid_until = quote_date + timedelta(days=20)
        valid_until_str = valid_until.strftime("%B %d, %Y")
    except:
        valid_until_str = "20 days from quotation date"
    
    header_data = [
        ['Quotation No:', quotation_number, 'Date:', date],
        ['Generated By:', generated_by, 'Valid Until:', valid_until_str]
    ]
    
    header_table = Table(header_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    elements.append(Paragraph("Bill To:", heading_style))
    customer_data = [
        ['Customer Name:', customer_name],
        ['Contact:', customer_contact]
    ]
    
    customer_table = Table(customer_data, colWidths=[1.5*inch, 5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Services table with serial number and quantity
    service_data = [['Sl No', 'Service Description', 'Qty', 'Rate', 'Amount']]
    subtotal = 0
    
    for sl_no, service, qty, cost in services:
        amount = qty * cost
        service_data.append([
            str(sl_no),
            service, 
            str(qty), 
            f'{currency_symbol}{cost:,.2f}',
            f'{currency_symbol}{amount:,.2f}'
        ])
        subtotal += amount
    
    service_table = Table(service_data, colWidths=[0.6*inch, 3.2*inch, 0.6*inch, 1.3*inch, 1.3*inch])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(service_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # Totals table
    totals_data = [['Subtotal:', f'{currency_symbol}{subtotal:,.2f}']]
    
    if tax_rate > 0:
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount
        totals_data.append([f'Tax (GST {tax_rate}%):', f'{currency_symbol}{tax_amount:,.2f}'])
        totals_data.append(['Total:', f'{currency_symbol}{total:,.2f}'])
    else:
        totals_data.append(['Total:', f'{currency_symbol}{subtotal:,.2f}'])
    
    totals_table = Table(totals_data, colWidths=[5.7*inch, 1.3*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(totals_table)
    
    # Add notes if provided
    if notes and notes.strip():
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Notes:", heading_style))
        # Split notes into lines and limit to 50 lines
        note_lines = notes.strip().split('\n')[:50]
        for line in note_lines:
            if line.strip():
                elements.append(Paragraph(line, small_text_style))
    
    # Extract email from customer contact for footer
    contact_email = customer_contact.split('|')[0].strip() if '|' in customer_contact else customer_contact.strip()
    
    # Add footer
    elements.append(Spacer(1, 0.4 * inch))
    elements.append(Paragraph("<b>Thank you for your Business!</b>", footer_style))
    elements.append(Paragraph(f"If you have any questions on this quote, please reach out to connect@openappservices.com", footer_small_style))
    
    doc.build(elements)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get form data
            company_name = request.form['company_name']
            quotation_number = request.form['quotation_number']
            date = request.form['date']
            generated_by = request.form['generated_by']
            customer_name = request.form['customer_name']
            customer_contact = request.form['customer_contact']
            tax_rate = float(request.form.get('tax_rate', 0))
            currency = request.form.get('currency', 'USD')
            notes = request.form.get('notes', '')
            
            # Get services with serial number and quantity
            service_sl = request.form.getlist('service_sl[]')
            service_descs = request.form.getlist('service_desc[]')
            service_qtys = request.form.getlist('service_qty[]')
            service_costs = request.form.getlist('service_cost[]')
            
            services = [
                (int(sl), desc, int(qty), float(cost)) 
                for sl, desc, qty, cost in zip(service_sl, service_descs, service_qtys, service_costs)
            ]
            
            # Generate PDF
            filename = f"/tmp/quotation_{quotation_number.replace('/', '_')}.pdf"
            create_quotation(
                company_name, quotation_number, date, generated_by,
                customer_name, customer_contact, services, tax_rate, 
                currency, notes, filename
            )
            
            return send_file(filename, as_attachment=True, download_name=f"quotation_{quotation_number}.pdf")
        
        except Exception as e:
            return f"Error: {str(e)}", 400
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)