from flask import Blueprint, send_file
from database.db_service import DBService
from services.pdf_services import generate_report_pdf
from utils.helpers import api_response

download_bp = Blueprint('download_bp', __name__)

@download_bp.route('/pdf/<report_id>', methods=['GET'])
def download_pdf(report_id):
    # 1. Fetch Data
    report = DBService.get_report_by_id(report_id)

    if not report or report.get('status') != 'analyzed':
        return api_response(False, "Report not ready or found", status_code=404)

    analysis_result = report.get("analysis_data", {})

    # 3. Generate PDF
    pdf_buffer = generate_report_pdf(report, analysis_result)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"report_{report_id}.pdf",
        mimetype='application/pdf'
    )
