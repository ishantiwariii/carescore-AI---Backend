from utils.helpers import parse_reference_range
from services.reference_service import prepare_test_for_analysis

def resolve_test_reference(test: dict, gender: str):
    """
    Priority:
    1. Lab-provided reference range (from confirmed_data)
    2. reference_range.json fallback
    """

    lab_range = parse_reference_range(test.get("reference_range"))

    if lab_range:
        return {
            "min": lab_range["min"],
            "max": lab_range["max"],
            "source": "lab"
        }

   
    ref_data = prepare_test_for_analysis(
        test_name_snake=test["test_name"],
        extracted_value=test["value"],
        extracted_unit=test["unit"],
        gender=gender
    )

    ref_range = ref_data.get("reference_range")

    if ref_range:
        return {
            "min": ref_range.get("min"),
            "max": ref_range.get("max"),
            "source": "standard"
        }

    return None
