import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_invoice_pdf(invoice) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph(f"<b>FACTURA {invoice.invoice_number}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Client info
    client_name = ""
    if hasattr(invoice, "client") and invoice.client:
        client_name = f"{invoice.client.first_name} {invoice.client.last_name}"
        if invoice.client.email:
            client_name += f"<br/>{invoice.client.email}"
        if invoice.client.phone:
            client_name += f"<br/>{invoice.client.phone}"
        if invoice.client.address:
            client_name += f"<br/>{invoice.client.address}"

    info_data = [
        ["Cliente:", Paragraph(client_name, styles["Normal"])],
        ["Fecha emision:", str(invoice.issue_date)],
        ["Fecha vencimiento:", str(invoice.due_date)],
        ["Estado:", invoice.status],
    ]
    info_table = Table(info_data, colWidths=[1.5 * inch, 4.5 * inch])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Items table
    items_header = ["Descripcion", "Cant.", "Precio Unit.", "Total"]
    items_data = [items_header]
    for item in invoice.items:
        items_data.append([
            item.description,
            str(item.quantity),
            f"${float(item.unit_price):.2f}",
            f"${float(item.total):.2f}",
        ])

    items_table = Table(items_data, colWidths=[3.5 * inch, 0.75 * inch, 1.25 * inch, 1.25 * inch])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 12))

    # Totals
    totals_data = [
        ["", "", "Subtotal:", f"${float(invoice.subtotal):.2f}"],
        ["", "", f"Impuesto ({float(invoice.tax_rate)}%):", f"${float(invoice.tax_amount):.2f}"],
        ["", "", "TOTAL:", f"${float(invoice.total):.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[3.5 * inch, 0.75 * inch, 1.25 * inch, 1.25 * inch])
    totals_table.setStyle(TableStyle([
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("LINEABOVE", (2, -1), (-1, -1), 1, colors.black),
    ]))
    elements.append(totals_table)

    if invoice.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Notas:</b>", styles["Normal"]))
        elements.append(Paragraph(invoice.notes, styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
