from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from io import BytesIO
import re

def generate_professional_pdf(filename, document_content):
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=72, bottomMargin=50)

    styles = getSampleStyleSheet()
    elements = []

    # Custom paragraph styles
    styles.add(ParagraphStyle(name='Justify', alignment=TA_LEFT, leading=15))
    styles.add(ParagraphStyle(name='Heading', fontSize=12, leading=16, spaceAfter=10, spaceBefore=10, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Signature', fontSize=10, leading=12, spaceBefore=30))

    # Split content into lines
    lines = document_content.strip().splitlines()

    # Build content
    for line in lines:
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 8))
            continue

        # Make headings bold
        if re.match(r"(?i)^To|^Subject|^Dear|^respected|^sincerely|^regards", line):
            elements.append(Paragraph(f"<b>{line}</b>", styles["Justify"]))
        else:
            elements.append(Paragraph(line, styles["Justify"]))

    # Signature lines
    elements.append(Spacer(1, 30))
    table = Table([
        ["_________________________", "_________________________"],
        ["Client Signature", "Advocate Signature"]
    ], colWidths=[250, 250])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
    ]))
    elements.append(table)

    doc.build(elements)

    # Save to file
    with open(filename, "wb") as f:
        f.write(buffer.getvalue())
