# app/tools/approval.py

def request_approval(reason: str) -> dict:
    """
    External approval trigger.
    Can later connect to:
    - Web UI
    - Slack
    - Email
    - Dashboard
    """

    return {
        "status": "pending",
        "reason": reason
    }