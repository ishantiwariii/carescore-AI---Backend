from utils.helpers import parse_reference_range
from services.reference_service import prepare_test_for_analysis

def resolve_test_reference(test: dict, gender: str):
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

    if ref_data.get("reference_range"):
        test["value"] = ref_data["normalized_value"]
        test["unit"] = ref_data["reference_unit"]

        return {
            "min": ref_data["reference_range"]["min"],
            "max": ref_data["reference_range"]["max"],
            "source": "standard"
        }

    return None
