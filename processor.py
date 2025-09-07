import json
from datetime import datetime

def validate_and_transform(log_str: str):
    """
    Validate and transform a single log entry.
    Returns: (log_dict, None) if valid OR (None, error_message) if invalid.
    """
    try:
        log = json.loads(log_str)
    except json.JSONDecodeError:
        return None, "Invalid JSON"

    required = ["timestamp", "user_id", "action"]
    if not all(k in log for k in required):
        return None, "Missing fields"

    try:
        # Input format: 2025-08-20T12:01:15Z (UTC)
        dt = datetime.strptime(log["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        # Output format: YYYY-MM-DD HH:MM:SS
        log["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        log["day_of_week"] = dt.strftime("%A")
    except ValueError:
        return None, "Invalid timestamp format"

    return log, None
