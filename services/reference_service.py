import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


TEST_ALIASES = {
    "hemoglobin": ["hemoglobin", "hb", "hgb"],
    "rbc_count": ["rbc", "rbc_count", "red_blood_cell"],
    "wbc_count": ["wbc", "wbc_count", "white_blood_cell"],
    "platelet_count": ["platelet", "platelets", "platelet_count"],
    "glucose_fasting": ["glucose_fasting", "fasting_blood_sugar", "fbs"],
    "hba1c": ["hba1c", "hb_a1c"],
    "creatinine": ["creatinine", "serum_creatinine"],
    "bun": ["bun", "blood_urea_nitrogen"],
    "egfr": ["egfr", "estimated_gfr"],
    "alt": ["alt", "sgpt"],
    "ast": ["ast", "sgot"],
    "alp": ["alp", "alkaline_phosphatase"],
    "bilirubin_total": ["bilirubin", "total_bilirubin"],
    "cholesterol_total": ["cholesterol", "total_cholesterol"],
    "hdl": ["hdl", "hdl_cholesterol"],
    "ldl": ["ldl", "ldl_cholesterol"],
    "triglycerides": ["triglycerides", "tg"]
}



REFERENCE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "reference_range.json"
)

with open(REFERENCE_PATH, "r") as f:
    REFERENCE_DATA = json.load(f)

def normalize_gender(gender: str | None) -> str | None:
    if not gender:
        return None

    g = gender.strip().lower()
    if g in ("m", "male"):
        return "male"
    if g in ("f", "female"):
        return "female"

    return None


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
    normalized_input = _normalize_test_name(test_name_snake)

    for category in REFERENCE_DATA:
        for test in category.get("tests", []):
            test_key = test.get("test_key")

            if not test_key:
                continue

            if normalized_input == test_key:
                return test

            aliases = TEST_ALIASES.get(test_key, [])
            if normalized_input in aliases:
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



def get_gender_reference_range(ref_test: dict, gender: str | None):
    ranges = ref_test.get("ranges", {})

    gender = normalize_gender(gender)

    if gender and gender in ranges:
        return ranges[gender]

    if "general" in ranges:
        return ranges["general"]

    return None




def prepare_test_for_analysis(
    test_name_snake: str,
    extracted_value: float,
    extracted_unit: str,
    gender: str | None
):
    ref = find_test_reference(test_name_snake)

    if not ref:
        return {
            "test_key": test_name_snake,
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
        "test_key": ref["test_key"],
        "display_name": ref.get("display_name"),
        "normalized_value": normalized_value,
        "normalized_unit": normalized_unit,
        "reference_range": ref_range,
        "reference_unit": standard_unit
    }
