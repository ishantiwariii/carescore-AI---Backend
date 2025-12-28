from flask import Blueprint, request
from database.db_service import get_report_by_id
from utils.helpers import api_response

compare_bp = Blueprint('compare_bp', __name__)

@compare_bp.route('/diff', methods=['POST'])
def compare_reports():
    data = request.json
    id_1 = data.get('report_id_1')
    id_2 = data.get('report_id_2')
    
    r1 = get_report_by_id(id_1)
    r2 = get_report_by_id(id_2)
    
    if not r1 or not r2:
        return api_response(False, "One or both reports not found", status_code=404)
        
    comparison = {}
    
    # Find common keys and calculate diff
    data1 = r1.get('confirmed_data', {})
    data2 = r2.get('confirmed_data', {})
    
    for key, val1 in data1.items():
        if key in data2:
            try:
                diff = float(val1) - float(data2[key])
                comparison[key] = {
                    "old": data2[key],
                    "new": val1,
                    "change": diff,
                    "trend": "up" if diff > 0 else "down"
                }
            except:
                pass # Skip non-numeric comparisons
                
    return api_response(True, "Comparison generated", comparison)