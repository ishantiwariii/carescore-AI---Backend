from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

def generate_report_pdf(report_data, analysis_result):
    """
    Creates a PDF file in memory.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Medical Analysis Report")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Date: {report_data.get('created_at', 'N/A')}")
    p.drawString(50, height - 85, f"CareScore: {analysis_result['care_score']}/100")

    # Disclaimer
    p.setFont("Helvetica-Oblique", 8)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawString(50, 50, "DISCLAIMER: This is an AI-generated summary, not a medical diagnosis. Consult a doctor.")
    p.setFillColorRGB(0, 0, 0)

    # Content
    y_position = height - 120
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_position, "Deviations Found:")
    y_position -= 20
    p.setFont("Helvetica", 10)

    for deviation in analysis_result['deviations']: # using 'metrics' list from analysis model
        p.drawString(70, y_position, f"- {deviation}")
        y_position -= 15

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer