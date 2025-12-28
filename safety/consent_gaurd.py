def verify_consent(request_data):
    """Ensures user explicitly accepted terms"""
    if not request_data.get('consent_accepted'):
        return False, "User consent is required to process medical data."
    return True, ""