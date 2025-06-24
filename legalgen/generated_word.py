# utils.py
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime

import re


def add_text_header_footer(canvas, doc, advocate):
    canvas.saveState()

    canvas.setFont("Helvetica-Bold", 12)
    education = advocate.education if advocate.education else ""
    canvas.drawString(50, A4[1] - 50, f"Advocate {advocate.name}{', ' + education if education else ''}")

    canvas.setFont("Helvetica", 9)

    y = A4[1] - 63

    if advocate.address:
        canvas.drawString(50, y, f"Address: {advocate.address}")
        y -= 13

    contact_line = []
    if advocate.email:
        contact_line.append(f"Email: {advocate.email}")
    if advocate.phone:
        contact_line.append(f"Mobile: {advocate.phone}")
    if contact_line:
        canvas.drawString(50, y, " | ".join(contact_line))
        y -= 13

    canvas.drawRightString(A4[0] - 50, A4[1] - 50, f"Date: {datetime.now().strftime('%d/%m/%Y')}")

    # Bold line
    canvas.setLineWidth(1.5)
    canvas.line(50, y - 5, A4[0] - 50, y - 5)

    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(A4[0] - 50, 30, f"Page {doc.page}")

    canvas.restoreState()


def generate_professional_pdf(buffer, document_content, advocate):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_LEFT, leading=15))
    styles.add(ParagraphStyle(name='Heading', fontSize=12, leading=16, spaceAfter=10, spaceBefore=10, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Signature', fontSize=10, leading=12, spaceBefore=30))

    elements = []
    lines = document_content.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 8))
            continue
        if re.match(r"(?i)^To|^Subject|^Dear|^respected|^sincerely|^regards", line):
            elements.append(Paragraph(f"<b>{line}</b>", styles["Justify"]))
        else:
            elements.append(Paragraph(line, styles["Justify"]))

    elements.append(Spacer(1, 30))
    table = Table([
        ["_________________________", "_________________________"],
        ["Advocate Signature", "Client Signature"]
    ], colWidths=[250, 250])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
    ]))
    elements.append(table)

    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=120, bottomMargin=60)

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='with-header-footer', frames=[frame],
                            onPage=lambda canvas, doc: add_text_header_footer(canvas, doc, advocate))
    doc.addPageTemplates([template])
    doc.build(elements)
    

