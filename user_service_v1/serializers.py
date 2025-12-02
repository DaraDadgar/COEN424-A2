def validate_user_payload(payload):
    if "email" not in payload:
        return "Missing email"
    if "address" not in payload:
        return "Missing address"
    return None

def validate_email(payload):
    if "email" not in payload:
        return "Missing email"
    return None

def validate_address(payload):
    if "address" not in payload:
        return "Missing address"
    return None
