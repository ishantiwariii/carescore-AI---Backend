import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

REFERENCE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "reference_range.json"
)

with open(REFERENCE_PATH, "r") as f:
    REFERENCE_DATA = json.load(f)



def _normalize_test_name(name: str) -> str:
    return (
        name.lower()
        .replace("(", "")
        .replace(")", "")
        .replace("/", " ")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
        .replace(" ", "_")
    )



def find_test_reference(test_name_snake: str):
    for category in REFERENCE_DATA:
        for test in category.get("tests", []):
            ref_name = _normalize_test_name(test["test"])
            if ref_name == test_name_snake:
                return test
    return None



def normalize_value_with_gemini(
    test_name: str,
    value: float,
    current_unit: str,
    target_unit: str
):
    if current_unit == target_unit:
        return value, target_unit

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
You are a medical unit conversion engine.

Convert the given lab test value to the target unit.

Rules:
- Perform only mathematical conversion
- No medical interpretation
- Return ONLY JSON

Input:
Test: {test_name}
Value: {value}
Current Unit: {current_unit}
Target Unit: {target_unit}

Output:
{{
  "normalized_value": number,
  "normalized_unit": "{target_unit}"
}}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip().replace("```json", "").replace("```", "")

    data = json.loads(content)
    return data["normalized_value"], data["normalized_unit"]



def get_gender_reference_range(ref_test: dict, gender: str):
    ranges = ref_test.get("ranges", {})
    gender = (gender or "unknown").lower()

    if gender in ranges and ranges[gender]["min"] is not None:
        return ranges[gender]

    # Fallback order
    for key in ["general", "male", "female"]:
        if key in ranges and ranges[key]["min"] is not None:
            return ranges[key]

    return None



def prepare_test_for_analysis(
    test_name_snake: str,
    extracted_value: float,
    extracted_unit: str,
    gender: str
):
    """
    Combines reference lookup + unit normalization + gender range selection.
    """

    ref = find_test_reference(test_name_snake)

    if not ref:
        return {
            "test_name": test_name_snake,
            "normalized_value": extracted_value,
            "normalized_unit": extracted_unit,
            "reference_range": None,
            "note": "Reference data not found"
        }

    standard_unit = ref["unit"]

    normalized_value, normalized_unit = normalize_value_with_gemini(
        test_name_snake,
        extracted_value,
        extracted_unit,
        standard_unit
    )

    ref_range = get_gender_reference_range(ref, gender)

    return {
        "test_name": test_name_snake,
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "reference_range": ref_range,
        "reference_unit": standard_unit
    }
