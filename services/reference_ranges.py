from utils.constants import DEFAULT_REFERENCE_RANGES

def get_reference_range(test_name, sex="male", age=30):
    """
    Returns the correct min/max for a specific patient demographic.
    Currently falls back to defaults, but structured for expansion.
    """
    # In a real app, you would have logic here:
    # if sex == "female" and test_name == "hemoglobin": return ...
    
    # For now, return default or None
    return DEFAULT_REFERENCE_RANGES.get(test_name.lower())