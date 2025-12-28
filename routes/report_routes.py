from flask import Blueprint, request, jsonify
from services.gemini_vision import extract_data_from_image
from database.storage import upload_file, get_public_url
from database.db_service import DBService
import uuid

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/upload', methods=['POST'])
def upload_report():
    """
    1. Uploads file to Supabase.
    2. Runs Gemini Vision to extract data.
    3. Creates 'pending_confirmation' report in DB.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    try:
        # 1. Upload
        file_ext = file.filename.split('.')[-1]
        file_path = f"{user_id}/{uuid.uuid4()}.{file_ext}"
        bucket_name = "reports"
        
        file_bytes = file.read()
        try:
            upload_file(bucket_name, file_path, file_bytes, file.content_type)
        except Exception as e:
            print("STORAGE UPLOAD FAILED:", e)
            return jsonify({
                "success": False,
                "error": "File upload failed"
            }), 403

        file_url = get_public_url(bucket_name, file_path)


        # 2. Extract
        extracted_data = extract_data_from_image(file_bytes)
        try:
            extracted_data = extract_data_from_image(file_bytes)
            ai_status = "ok"

        except Exception as e:
            # Handle Gemini quota or vision failure
            if "RESOURCE_EXHAUSTED" in str(e):
                extracted_data = {}
                ai_status = "quota_exhausted"
            else:
                raise
        # 3. Create Report
        report = DBService.create_report(user_id, file_url, extracted_data)

        if not report or "id" not in report:
            raise Exception("Report insert failed: no ID returned")


        return jsonify({
            "success": True,
            "report_id": report['id'],
            "extracted_data": extracted_data,
            "image_url": file_url
        })

    except Exception as e:
        print("UPLOAD ROUTE ERROR:", e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
