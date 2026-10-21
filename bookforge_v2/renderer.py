"""PDF rendering engine shared by all BookForge book templates."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import BookConfig
from .templates import BookTemplate


def render_book(config: BookConfig, template: BookTemplate, output_path: str | Path) -> Path:
    """Render a configured book to PDF and return its output path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        str(destination), pagesize=letter,
        rightMargin=0.55 * inch, leftMargin=0.55 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
    )
    story = [Paragraph(config.title, styles["Title"]), Spacer(1, 0.15 * inch)]
    if config.subtitle.strip():
        story.extend([Paragraph(config.subtitle, styles["Normal"]), Spacer(1, 0.3 * inch)])
    for index, page in enumerate(template.build_pages(config.page_count)):
        if index > 0 or story:
            story.append(PageBreak())
        story.append(Paragraph(page.heading, styles["Heading2"]))
        table_data = [list(page.columns), *[list(row) for row in page.rows]]
        table = Table(table_data, repeatRows=1, colWidths=[1.1 * inch, 0.9 * inch, 2.3 * inch, 0.7 * inch, 1.1 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263746")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9AA5AE")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)
    document.build(story)
    return destination
