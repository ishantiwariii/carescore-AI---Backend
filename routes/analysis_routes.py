from flask import Blueprint, request, jsonify
from services.analytics_engine import calculate_care_score
from services.gemini_text import generate_health_explanation
from database.db_service import DBService

# 👇 import the Gemini/LangChain error
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

analysis_bp = Blueprint('analysis_bp', __name__)

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_report():
    """
    Receives confirmed data -> Calculates Score -> Explains -> Updates DB
    Gracefully handles AI quota exhaustion.
    """
    data = request.json
    report_id = data.get('report_id')
    confirmed_data = data.get('confirmed_data')

    if not report_id or not confirmed_data:
        return jsonify({"error": "Missing report_id or data"}), 400

    # 1. Math Analysis (ALWAYS WORKS)
    analytics = calculate_care_score(confirmed_data)

    # 2. AI Explanation (MAY FAIL)
    try:
        explanation = generate_health_explanation(
            confirmed_data,
            analytics['deviations']
        )
        ai_status = "ok"

    except ChatGoogleGenerativeAIError as e:
        # 🔥 Gemini quota exhausted or similar
        if "RESOURCE_EXHAUSTED" in str(e):
            explanation = {
                "summary": "AI explanation temporarily unavailable.",
                "note": "Your report data is saved. Please retry later.",
            }
            ai_status = "quota_exhausted"
        else:
            # Unknown AI error → real bug
            raise

    # 3. Save Results (ALWAYS SAVE)
    analysis_result = {
        "care_score": analytics['score'],
        "deviations": analytics['deviations'],
        "explanation": explanation,
        "ai_status": ai_status,  # 👈 useful for frontend
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
