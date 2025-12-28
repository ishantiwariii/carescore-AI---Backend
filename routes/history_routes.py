from flask import Blueprint, request, jsonify
from database.db_service import DBService

history_bp = Blueprint('history_bp', __name__)

@history_bp.route('/list', methods=['GET'])
def list_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    history = DBService.get_user_history(user_id)
    return jsonify({"success": True, "data": history})

@history_bp.route('/<report_id>', methods=['GET'])
def get_report(report_id):
    report = DBService.get_report_by_id(report_id)

    if not report:
        return jsonify({
            "success": False,
            "error": "Report not found"
        }), 404

    return jsonify({
        "success": True,
        "data": report
    })
