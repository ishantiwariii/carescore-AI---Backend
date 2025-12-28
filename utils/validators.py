def validate_lab_values(data):
    """Basic sanity check for numbers"""
    valid_data = {}
    errors = []
    
    for key, value in data.items():
        try:
            # Attempt to convert to float
            num_val = float(value)
            if num_val < 0:
                errors.append(f"{key} cannot be negative.")
            else:
                valid_data[key] = num_val
        except ValueError:
            errors.append(f"{key} is not a valid number.")
            
    return valid_data, errors