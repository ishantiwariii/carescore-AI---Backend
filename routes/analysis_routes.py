from flask import Blueprint, request, jsonify
from services.analytics_engine import calculate_care_score
from services.gemini_text import generate_health_explanation
from database.db_service import DBService
from services.reference_resolver import resolve_test_reference
from utils.helpers import format_reference_range
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from services.reference_service import normalize_gender

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_report():
    data = request.json
    report_id = data.get('report_id')
    confirmed_data = data.get('confirmed_data')

    if not report_id or not confirmed_data:
        return jsonify({"error": "Missing report_id or data"}), 400

    
    gender = normalize_gender(
    confirmed_data.get("patient", {}).get("gender")
)

    for test in confirmed_data.get("tests", []):
        resolved = resolve_test_reference(test, gender)

        test["reference_range"] = (
            format_reference_range(resolved, test.get("unit"))
            if resolved else "Reference not available"
        )


    
    analytics_response = calculate_care_score(
                            confirmed_data.get("tests", [])
                        )


    if not analytics_response.get("success"):
        return jsonify({
            "success": False,
            "error": analytics_response.get("error"),
            "message": analytics_response.get("message"),
        }), 503

    analytics = analytics_response["data"]

    
    try:
        explanation_resp = generate_health_explanation(
            confirmed_data,
            analytics['deviations']
        )

        explanation = (
            explanation_resp.get("content")
            if isinstance(explanation_resp, dict)
            else explanation_resp
        )

        ai_status = "ok"

    except ChatGoogleGenerativeAIError as e:
        if "RESOURCE_EXHAUSTED" in str(e):
            explanation = (
                "AI explanation temporarily unavailable. "
                "Your report data is saved. Please retry later."
            )
            ai_status = "quota_exhausted"
        else:
            raise

    
    analysis_result = {
        "care_score": analytics['score'],
        "deviations": analytics['deviations'],
        "explanation": explanation,
        "ai_status": ai_status,
    }

    DBService.update_report_status(
        report_id,
        "analyzed",
        confirmed_data,
        analysis_result
    )

    return jsonify({
        "success": True,
        "data": analysis_result
    })
