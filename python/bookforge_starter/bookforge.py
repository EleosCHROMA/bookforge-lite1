"""BookForge Lite: generate a simple, print-friendly vehicle maintenance logbook PDF."""

from pathlib import Path
import argparse
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)


def validate_inputs(vehicle_name: str, records: int) -> None:
    """Validate user-supplied options before creating a file."""
    if not isinstance(vehicle_name, str) or not vehicle_name.strip():
        raise ValueError("vehicle_name must not be empty.")
    if not isinstance(records, int) or isinstance(records, bool) or records < 1:
        raise ValueError("records must be a positive integer.")
    if records > 250:
        raise ValueError("records must be 250 or fewer for this starter version.")


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="BookTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=26, leading=32, alignment=TA_CENTER, spaceAfter=18
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCenter", parent=styles["Normal"], fontSize=12,
        leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#444444")
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading2"], fontSize=15,
        leading=19, spaceBefore=8, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name="SmallNote", parent=styles["Normal"], fontSize=8, leading=11,
        textColor=colors.HexColor("#555555")
    ))
    return styles


def page_decorations(canvas, doc):
    """Draw a light header and page number on every interior page."""
    canvas.saveState()
    page_width, page_height = letter
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#BBBBBB"))
        canvas.setLineWidth(0.5)
        canvas.line(0.65 * inch, page_height - 0.55 * inch,
                    page_width - 0.65 * inch, page_height - 0.55 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.drawString(0.65 * inch, page_height - 0.42 * inch,
                          "VEHICLE MAINTENANCE LOG")
        canvas.drawRightString(page_width - 0.65 * inch, 0.38 * inch,
                               f"Page {doc.page}")
    canvas.restoreState()


def line_table(labels, widths):
    rows = [[Paragraph(f"<b>{escape(label)}</b>", getSampleStyleSheet()["BodyText"])
             for label in labels]]
    # Empty writing rows with a little vertical room.
    rows.extend([["" for _ in labels] for _ in range(3)])
    table = Table(rows, colWidths=widths, rowHeights=[0.34 * inch, 0.45 * inch,
                                                      0.45 * inch, 0.45 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#777777")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def build_logbook(output_path, vehicle_name="My Vehicle", records=40, subtitle=""):
    """Create a printable PDF logbook and return the output path."""
    validate_inputs(vehicle_name, records)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    story = []

    # Cover/title page
    story.append(Spacer(1, 1.5 * inch))
    story.append(Paragraph("VEHICLE<br/>MAINTENANCE LOGBOOK", styles["BookTitle"]))
    story.append(Spacer(1, 0.2 * inch))
    if subtitle:
        safe_subtitle = escape(subtitle.strip())
        story.append(Paragraph(safe_subtitle, styles["SubtitleCenter"]))
        story.append(Spacer(1, 0.2 * inch))
    safe_name = escape(vehicle_name.strip())
    story.append(Paragraph(f"Personal service records for: <b>{safe_name}</b>",
                           styles["SubtitleCenter"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "Track service dates, mileage, parts, costs, and notes in one place.",
        styles["SubtitleCenter"]))
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("Owner: __________________________________________",
                           styles["SubtitleCenter"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Keep receipts and follow your vehicle manufacturer's service schedule.",
                           styles["SmallNote"]))
    story.append(PageBreak())

    # Vehicle information page
    story.append(Paragraph("Vehicle Information", styles["SectionHeading"]))
    info_rows = [
        ["Make / Model", "", "Year", ""],
        ["VIN (optional)", "", "License Plate", ""],
        ["Purchase Date", "", "Current Mileage", ""],
        ["Preferred Shop", "", "Phone", ""],
        ["Tire Size", "", "Oil Specification", ""],
    ]
    info_table = Table(info_rows, colWidths=[1.15*inch, 2.15*inch, 1.05*inch, 2.0*inch],
                       rowHeights=[0.58*inch]*len(info_rows))
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#777777")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEEEEE")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#EEEEEE")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Service reminders", styles["SectionHeading"]))
    story.append(Paragraph(
        "Use this area to record reminders from your owner's manual or trusted mechanic. "
        "Intervals vary by vehicle and driving conditions.", styles["Normal"]))
    story.append(Spacer(1, 0.15 * inch))
    story.append(line_table(["Service / Reminder", "Due at mileage", "Due date"],
                            [2.8*inch, 1.5*inch, 2.05*inch]))
    story.append(PageBreak())

    # One record per page keeps the layout simple and writable.
    for number in range(1, records + 1):
        story.append(Paragraph(f"Maintenance Record {number:02d}",
                               styles["SectionHeading"]))
        story.append(Paragraph(
            "Record completed work and retain any related receipts.", styles["SmallNote"]))
        story.append(Spacer(1, 0.15 * inch))
        story.append(line_table(
            ["Date", "Odometer", "Service / Repair"],
            [1.25*inch, 1.35*inch, 3.75*inch]))
        story.append(Spacer(1, 0.18 * inch))
        story.append(line_table(
            ["Parts / Supplies", "Labor / Shop"],
            [3.18*inch, 3.17*inch]))
        story.append(Spacer(1, 0.18 * inch))
        story.append(Paragraph("Cost summary", styles["Normal"]))
        story.append(line_table(
            ["Parts cost", "Labor cost", "Total cost"],
            [2.1*inch, 2.1*inch, 2.15*inch]))
        story.append(Spacer(1, 0.18 * inch))
        story.append(Paragraph("Notes", styles["Normal"]))
        notes = Table([[""], [""], [""], [""]], colWidths=[6.35*inch],
                      rowHeights=[0.38*inch]*4)
        notes.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#777777")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ]))
        story.append(notes)
        if number < records:
            story.append(PageBreak())

    doc = SimpleDocTemplate(
        str(output), pagesize=letter,
        rightMargin=0.65*inch, leftMargin=0.65*inch,
        topMargin=0.75*inch, bottomMargin=0.65*inch,
        title=f"Vehicle Maintenance Logbook - {vehicle_name.strip()}",
        author="BookForge Lite"
    )
    doc.build(story, onFirstPage=page_decorations, onLaterPages=page_decorations)
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Generate a printable vehicle maintenance logbook PDF."
    )
    parser.add_argument("--subtitle", type=str,
                        help="Subtitle of the book")
    parser.add_argument("--vehicle", default="My Vehicle",
                        help='Vehicle label shown on the title page (default: "My Vehicle").')
    parser.add_argument("--records", type=int, default=40,
                        help="Number of maintenance-record pages (1-250; default: 40).")
    parser.add_argument("--output", default="output/vehicle_maintenance_logbook.pdf",
                        help="Output PDF path.")
    args = parser.parse_args()
    try:
        path = build_logbook(args.output, args.vehicle, args.records, args.subtitle)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Created PDF: {path.resolve()}")
    print(f"Maintenance record pages: {args.records}")


if __name__ == "__main__":
    main()
