# Simplified reference ranges for the example
DEFAULT_REFERENCE_RANGES = {
    "hemoglobin": {"min": 13.0, "max": 17.0, "unit": "g/dL"},
    "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
    "cholesterol": {"min": 125, "max": 200, "unit": "mg/dL"}
}

def calculate_care_score(data):
    """
    Calculates score (0-100) based on deviations[cite: 91].
    """
    total_score = 100
    deviations = []

    for test, value in data.items():
        try:
            val = float(value)
        except:
            continue

        ref = DEFAULT_REFERENCE_RANGES.get(test.lower())
        if ref:
            if val < ref['min']:
                deviations.append(f"{test} is Low")
                total_score -= 10 # Simple penalty
            elif val > ref['max']:
                deviations.append(f"{test} is High")
                total_score -= 10

    return {
        "score": max(0, total_score),
        "deviations": deviations
    }