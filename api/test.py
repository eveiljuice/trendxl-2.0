"""
Minimal test handler for Vercel
"""

def handler(event, context):
    return {
        'statusCode': 200,
        'body': '{"status": "ok", "message": "Minimal Python handler works!"}'
    }

