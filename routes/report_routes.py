from flask import Blueprint, request, jsonify
from services.gemini_vision import extract_data_from_image
from database.storage import upload_file, get_public_url
from database.db_service import DBService
import uuid

report_bp = Blueprint('report_bp', __name__)

@report_bp.route("/upload", methods=["POST"])
def upload_report():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    user_id = request.form.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "User ID required"}), 400

    try:
        
        file_ext = file.filename.split(".")[-1]
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        bucket_name = "reports"

        file_bytes = file.read()

        upload_file(bucket_name, file_path, file_bytes, file.content_type)
        file_url = get_public_url(bucket_name, file_path)

        
        extraction_result = extract_data_from_image(file_bytes)

        
        if not extraction_result.get("success"):
            return jsonify({
                "success": False,
                "error": extraction_result.get("error"),
                "message": extraction_result.get("message")
            }), 429 if extraction_result.get("error") == "QUOTA_EXHAUSTED" else 400

        extracted_data = extraction_result["data"]

        
        report = DBService.create_report(
            user_id=user_id,
            file_url=file_url,
            raw_data=extracted_data,
            status="pending_confirmation"
        )

        if not report or "id" not in report:
            raise Exception("Report insert failed")

        return jsonify({
            "success": True,
            "report_id": report["id"]
        })

    except Exception as e:
        print("UPLOAD ROUTE ERROR:", e)
        return jsonify({
            "success": False,
            "error": "UPLOAD_FAILED",
            "message": str(e)
        }), 500
