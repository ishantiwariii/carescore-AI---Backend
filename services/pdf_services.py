import io
from datetime import datetime

import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def normalize_explanation(explanation):
    """
    Ensures explanation is always a clean string for PDF rendering.
    Handles string, dict (Gemini-style), or anything else safely.
    """
    if isinstance(explanation, str):
        text = explanation
    elif isinstance(explanation, dict):
        text = (
            explanation.get("content")
            or explanation.get("summary")
            or explanation.get("message")
            or ""
        )
    else:
        text = str(explanation or "")

    return text.strip()




def generate_biomarker_chart(tests):
    labels = []
    values = []

    for test in tests:
        try:
            value = float(test.get("value"))
            labels.append(
                test.get("test_name", "")
                .replace("_", " ")
                .title()
            )
            values.append(value)
        except (TypeError, ValueError):
            continue

    if not values:
        return None

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, values)

    ax.set_title("Biomarker Overview")
    ax.set_ylabel("Value")
    ax.set_xlabel("Test")

    ax.tick_params(axis="x", rotation=45, labelsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png", dpi=150)
    plt.close(fig)

    img_buffer.seek(0)
    return img_buffer




def generate_report_pdf(report_data, analysis_result):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Medical Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))

    created_at = report_data.get("created_at")
    created_at = (
        str(created_at)
        if created_at
        else datetime.now().strftime("%Y-%m-%d")
    )

    story.append(Paragraph(f"<b>Date:</b> {created_at}", styles["Normal"]))
    story.append(
        Paragraph(
            f"<b>CareScore:</b> {analysis_result.get('care_score', 'N/A')} / 100",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 20))

    explanation_raw = analysis_result.get("explanation")
    explanation_text = normalize_explanation(explanation_raw)

    if explanation_text:
        story.append(Paragraph("AI Summary", styles["Heading2"]))
        story.append(Spacer(1, 6))

        explanation_text = explanation_text.replace("\n\n", "<br/><br/>")
        explanation_text = explanation_text.replace("\n", "<br/>")

        story.append(
            Paragraph(explanation_text, styles["BodyText"])
        )
        story.append(Spacer(1, 18))

    raw_deviations = analysis_result.get("deviations", [])

    deviation_list = []

    if isinstance(raw_deviations, dict):
        deviation_list = [
            f"{test.replace('_', ' ').title()} ({status})"
            for test, status in raw_deviations.items()
            if status != "normal"
        ]

    elif isinstance(raw_deviations, list):
        deviation_list = raw_deviations

    if deviation_list:
        story.append(Paragraph("Deviations Detected", styles["Heading2"]))
        story.append(Spacer(1, 6))

        for dev in deviation_list:
            story.append(
                Paragraph(f"• {dev}", styles["BodyText"])
            )

        story.append(Spacer(1, 18))


    tests = report_data.get("confirmed_data", {}).get("tests", [])

    if tests:
        story.append(Paragraph("Test Results", styles["Heading2"]))
        story.append(Spacer(1, 8))

        table_data = [
            ["Test", "Value", "Unit", "Reference Range"]
        ]

        for t in tests:
            table_data.append([
                t.get("test_name", "")
                .replace("_", " ")
                .title(),
                str(t.get("value", "")),
                t.get("unit", "—"),
                t.get("reference_range", "—")
            ])

        table = Table(
            table_data,
            colWidths=[160, 80, 80, 140]
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ]))

        story.append(table)
        story.append(Spacer(1, 20))

    chart_img = generate_biomarker_chart(tests)
    if chart_img:
        story.append(Paragraph("Biomarker Chart", styles["Heading2"]))
        story.append(Spacer(1, 10))
        story.append(Image(chart_img, width=460, height=300))
        story.append(Spacer(1, 20))

    story.append(Spacer(1, 30))
    story.append(
        Paragraph(
            "<i>"
            "Disclaimer: This report is generated using AI and is not a medical diagnosis. "
            "Always consult a qualified healthcare professional."
            "</i>",
            styles["Italic"]
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer
