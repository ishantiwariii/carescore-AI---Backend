# Fixed values to keep things consistent
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload

# Safety Keywords to filter out [cite: 129]
FORBIDDEN_KEYWORDS = [
    "cancer", "tumor", "hiv", "aids", "leukemia", 
    "take this medicine", "prescription", "diagnose",
    "consult immediately", "emergency"
]

# Standard reference ranges (fallback) [cite: 95]
DEFAULT_REFERENCE_RANGES = {
    "hemoglobin": {"min": 13.0, "max": 17.0, "unit": "g/dL"},
    "glucose_fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
    # Add more standard ranges here
}