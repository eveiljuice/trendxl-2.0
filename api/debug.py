"""
Debug handler to identify import issues
"""
import sys
import os
import traceback

def handler(event, context):
    """Debug handler that tests imports step by step"""
    logs = []
    status = "ok"
    error_detail = None
    
    try:
        logs.append("Step 1: Basic imports OK")
        
        # Test backend path
        backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
        logs.append(f"Step 2: Backend path = {backend_path}")
        logs.append(f"Step 2.1: Backend exists = {os.path.exists(backend_path)}")
        
        # Add to sys.path
        sys.path.insert(0, backend_path)
        logs.append("Step 3: Added backend to sys.path")
        
        # Try importing config
        try:
            from config import settings
            logs.append(f"Step 4: Config imported OK, debug={settings.debug}")
        except Exception as e:
            logs.append(f"Step 4 FAILED: Config import error: {str(e)}")
            raise
        
        # Try importing models
        try:
            from models import HealthCheckResponse
            logs.append("Step 5: Models imported OK")
        except Exception as e:
            logs.append(f"Step 5 FAILED: Models import error: {str(e)}")
            raise
        
        # Try importing database
        try:
            import database
            logs.append("Step 6: Database imported OK")
        except Exception as e:
            logs.append(f"Step 6 FAILED: Database import error: {str(e)}")
            raise
        
        # Try importing main
        try:
            from main import app
            logs.append("Step 7: Main app imported OK")
        except Exception as e:
            logs.append(f"Step 7 FAILED: Main app import error: {str(e)}")
            logs.append(f"Traceback: {traceback.format_exc()}")
            raise
        
        # Try importing mangum
        try:
            from mangum import Mangum
            logs.append("Step 8: Mangum imported OK")
        except Exception as e:
            logs.append(f"Step 8 FAILED: Mangum import error: {str(e)}")
            raise
        
        # Try creating handler
        try:
            test_handler = Mangum(app, lifespan="off")
            logs.append("Step 9: Mangum handler created OK")
        except Exception as e:
            logs.append(f"Step 9 FAILED: Handler creation error: {str(e)}")
            raise
        
        logs.append("SUCCESS: All imports completed!")
        
    except Exception as e:
        status = "error"
        error_detail = str(e)
        logs.append(f"CRITICAL ERROR: {error_detail}")
        logs.append(f"Full traceback: {traceback.format_exc()}")
    
    return {
        'statusCode': 200 if status == "ok" else 500,
        'headers': {'Content-Type': 'application/json'},
        'body': f'{{"status": "{status}", "error": {repr(error_detail)}, "logs": {logs}}}'
    }

