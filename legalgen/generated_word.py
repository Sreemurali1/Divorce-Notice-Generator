# Module: generated_word.py

# Import Necessary Libaries
from docx import Document

# Function for creating a word.DOCX
def generate_wordpad(filename, document_content):
    """
    Generate a Word document with structured format.
    """
    # Create a new Word document
    doc = Document()

    # Split the document by lines to add them in a structured way
    lines = document_content.splitlines()

    for line in lines:
        if line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("- "):
            # Bullet points
            doc.add_paragraph(line[2:], style='List Bullet')
        elif line.startswith("**") and "**" in line[2:]:
            # Handle bold segments
            parts = line.split("**")
            para = doc.add_paragraph()
            bold = False
            for p in parts:
                if bold:
                    para.add_run(p).bold = True
                else:
                    para.add_run(p)
                bold = not bold
        else:
            # Just add normal text
            doc.add_paragraph(line)

    # Save the Word document
    doc.save(filename)
