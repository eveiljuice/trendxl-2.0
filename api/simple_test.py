"""
Simple test endpoint to check Python runtime
"""


def handler(request):
    """Simple test handler"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"status": "ok", "message": "Python is working!"}'
    }
