def verify_confirmation(report_status):
    """Ensures data was reviewed by human before AI analysis"""
    if report_status != "confirmed":
        return False, "Data must be user-confirmed before analysis."
    return True, ""