from flask import jsonify
import re

def api_response(success, message, data=None, status_code=200):
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code


def parse_reference_range(range_str: str):
    """
    Converts lab reference range string into a dict:
    Examples:
      "13 - 17"        -> {"min": 13.0, "max": 17.0}
      "4,800 - 10,800"-> {"min": 4800.0, "max": 10800.0}
      "< 2"            -> {"min": None, "max": 2.0}
      "> 5"            -> {"min": 5.0, "max": None}
    """
    if not range_str or not isinstance(range_str, str):
        return None

    s = range_str.replace(",", "").strip()

    # a - b
    match = re.match(r"(\d+(\.\d+)?)\s*-\s*(\d+(\.\d+)?)", s)
    if match:
        return {
            "min": float(match.group(1)),
            "max": float(match.group(3))
        }

    # < x
    match = re.match(r"<\s*(\d+(\.\d+)?)", s)
    if match:
        return {
            "min": None,
            "max": float(match.group(1))
        }

    # > x
    match = re.match(r">\s*(\d+(\.\d+)?)", s)
    if match:
        return {
            "min": float(match.group(1)),
            "max": None
        }

    return None

def format_reference_range(ref: dict, unit: str):
    if not ref:
        return None

    min_v = ref.get("min")
    max_v = ref.get("max")

    if min_v is not None and max_v is not None:
        return f"{min_v} - {max_v} {unit}"
    if min_v is None and max_v is not None:
        return f"< {max_v} {unit}"
    if min_v is not None and max_v is None:
        return f"> {min_v} {unit}"

    return None

