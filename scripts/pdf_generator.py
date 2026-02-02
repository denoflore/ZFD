#!/usr/bin/env python3
"""
PDF Generator - Create complete Voynich Croatian translation PDF
"""

import re
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Try to register a Unicode font for Croatian characters
try:
    pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    FONT_NAME = 'DejaVu'
except:
    FONT_NAME = 'Helvetica'


def create_styles():
    """Create paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CroatianTitle',
        fontName=FONT_NAME,
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center
    ))

    styles.add(ParagraphStyle(
        name='CroatianHeading',
        fontName=FONT_NAME,
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue,
    ))

    styles.add(ParagraphStyle(
        name='CroatianSubheading',
        fontName=FONT_NAME,
        fontSize=12,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.darkgray,
    ))

    styles.add(ParagraphStyle(
        name='CroatianBody',
        fontName=FONT_NAME,
        fontSize=10,
        spaceAfter=6,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name='CroatianLabel',
        fontName=FONT_NAME,
        fontSize=9,
        spaceAfter=3,
        textColor=colors.darkgreen,
        leftIndent=20,
    ))

    styles.add(ParagraphStyle(
        name='CroatianFolio',
        fontName=FONT_NAME,
        fontSize=11,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.darkred,
        borderWidth=1,
        borderColor=colors.lightgrey,
        borderPadding=5,
    ))

    return styles


def escape_text(text):
    """Escape special characters for ReportLab."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def read_folio(filepath):
    """Read a converted folio file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse structure
    result = {'folio_id': '', 'labels': [], 'text': []}

    lines = content.split('\n')
    section = None

    for line in lines:
        if line.startswith('=== Folio'):
            match = re.search(r'Folio (\S+)', line)
            if match:
                result['folio_id'] = match.group(1)
        elif line == '[Labels]':
            section = 'labels'
        elif line == '[Text]':
            section = 'text'
        elif line.strip() and section:
            result[section].append(line)

    return result


def generate_pdf(output_path):
    """Generate the complete PDF."""
    print("Generating PDF...")

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = create_styles()
    story = []

    # =========================================================================
    # TITLE PAGE
    # =========================================================================
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("VOYNICH MANUSCRIPT", styles['CroatianTitle']))
    story.append(Paragraph("Croatian Translation", styles['CroatianHeading']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(
        "Orthographic conversion using the ZFD Character Mapping",
        styles['CroatianBody']
    ))
    story.append(Spacer(1, inch))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d')}",
        styles['CroatianBody']
    ))
    story.append(Paragraph(
        "ZFD Project - Zuger Functional Decipherment",
        styles['CroatianBody']
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHARACTER MAPPING REFERENCE
    # =========================================================================
    story.append(Paragraph("Character Mapping Reference", styles['CroatianHeading']))
    story.append(Spacer(1, 0.2*inch))

    # Operators
    story.append(Paragraph("Word-Initial Operators", styles['CroatianSubheading']))
    op_data = [
        ['EVA', 'Croatian', 'Function'],
        ['qo-', 'ko-', 'which/who (relative)'],
        ['ch-', 'h-', 'prefix/directional'],
        ['sh-', 'š-', 'with (comitative)'],
    ]
    op_table = Table(op_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    op_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(op_table)
    story.append(Spacer(1, 0.2*inch))

    # Gallows
    story.append(Paragraph("Gallows → Consonant Clusters", styles['CroatianSubheading']))
    gal_data = [
        ['EVA', 'Croatian', 'Notes'],
        ['k', 'st', 'Produces "kost" (bone)'],
        ['t', 'tr', 'Common in recipes'],
        ['f', 'pr', 'Less common'],
        ['p', 'pl', 'Rare'],
    ]
    gal_table = Table(gal_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    gal_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(gal_table)
    story.append(Spacer(1, 0.2*inch))

    # Suffixes
    story.append(Paragraph("Word-Final Suffixes", styles['CroatianSubheading']))
    suf_data = [
        ['EVA', 'Croatian', 'Function'],
        ['-y', '-i', 'adjectival ending'],
        ['-n', '-n', 'noun ending'],
        ['-r', '-r', 'agent suffix'],
        ['-l', '-l', 'noun ending'],
        ['-m', '-m', 'instrumental'],
    ]
    suf_table = Table(suf_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    suf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(suf_table)
    story.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    story.append(Paragraph("Table of Contents", styles['CroatianHeading']))
    story.append(Spacer(1, 0.2*inch))

    sections = [
        ('Herbal Section (Botanical)', 'herbal_a', 'f1r - f66v'),
        ('Astronomical Section', 'astronomical', 'f67r - f73v'),
        ('Biological Section', 'biological', 'f75r - f84v'),
        ('Pharmaceutical Section', 'pharmaceutical', 'f87r - f102v'),
        ('Recipe Section', 'recipes', 'f103r - f116v'),
    ]

    toc_data = [['Section', 'Folios']]
    for name, _, folios in sections:
        toc_data.append([name, folios])

    toc_table = Table(toc_data, colWidths=[4*inch, 2*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # =========================================================================
    # MANUSCRIPT CONTENT
    # =========================================================================
    base_dir = Path('voynich_data/croatian')

    for section_name, section_dir, _ in sections:
        story.append(Paragraph(section_name, styles['CroatianHeading']))
        story.append(Spacer(1, 0.1*inch))

        section_path = base_dir / section_dir
        if not section_path.exists():
            story.append(Paragraph(f"[Section not found: {section_dir}]", styles['CroatianBody']))
            continue

        # Sort folios numerically
        folio_files = sorted(
            section_path.glob('*.txt'),
            key=lambda p: (
                int(re.search(r'f(\d+)', p.stem).group(1)),
                p.stem[-1] if p.stem[-1] in 'rv' else 'a'
            )
        )

        for folio_path in folio_files:
            try:
                folio = read_folio(folio_path)

                # Folio header
                story.append(Paragraph(
                    f"Folio {folio['folio_id']}",
                    styles['CroatianFolio']
                ))

                # Labels (if any)
                if folio['labels']:
                    story.append(Paragraph("[Labels]", styles['CroatianSubheading']))
                    for label in folio['labels'][:20]:  # Limit labels
                        story.append(Paragraph(
                            escape_text(label),
                            styles['CroatianLabel']
                        ))

                # Text
                if folio['text']:
                    story.append(Paragraph("[Text]", styles['CroatianSubheading']))
                    for line in folio['text']:
                        story.append(Paragraph(
                            escape_text(line),
                            styles['CroatianBody']
                        ))

                story.append(Spacer(1, 0.1*inch))

            except Exception as e:
                story.append(Paragraph(
                    f"[Error reading {folio_path.name}: {e}]",
                    styles['CroatianBody']
                ))

        story.append(PageBreak())

    # =========================================================================
    # BUILD PDF
    # =========================================================================
    print("Building PDF document...")
    doc.build(story)
    print(f"PDF saved: {output_path}")

    return output_path


if __name__ == "__main__":
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)

    pdf_path = output_dir / 'voynich_croatian_complete.pdf'
    generate_pdf(pdf_path)

    # Print file size
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"File size: {size_mb:.2f} MB")
