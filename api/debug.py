"""
Debug FastAPI handler to identify import issues
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum
import sys
import os
import traceback

app = FastAPI()

@app.get("/debug")
def debug():
    """Debug endpoint that tests imports step by step"""
    logs = []
    status = "ok"
    error_detail = None
    
    try:
        logs.append("Step 1: FastAPI and basic imports OK")
        logs.append(f"Step 1.1: Python version = {sys.version}")
        logs.append(f"Step 1.2: Current dir = {os.getcwd()}")
        logs.append(f"Step 1.3: __file__ = {__file__}")
        
        # Test backend path
        backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
        logs.append(f"Step 2: Backend path = {backend_path}")
        logs.append(f"Step 2.1: Backend exists = {os.path.exists(backend_path)}")
        
        if os.path.exists(backend_path):
            backend_files = os.listdir(backend_path)
            logs.append(f"Step 2.2: Backend files = {backend_files[:10]}")  # First 10 files
        
        # Add to sys.path
        sys.path.insert(0, backend_path)
        logs.append("Step 3: Added backend to sys.path")
        logs.append(f"Step 3.1: sys.path[:3] = {sys.path[:3]}")
        
        # Try importing config
        try:
            from config import settings
            logs.append(f"Step 4: Config imported OK, debug={settings.debug}")
            logs.append(f"Step 4.1: OpenAI key exists = {bool(settings.openai_api_key)}")
            logs.append(f"Step 4.2: Ensemble key exists = {bool(settings.ensemble_api_token)}")
        except Exception as e:
            logs.append(f"Step 4 FAILED: Config import error: {str(e)}")
            logs.append(f"Step 4.1: Traceback: {traceback.format_exc()}")
            raise
        
        # Try importing models
        try:
            from models import HealthCheckResponse
            logs.append("Step 5: Models imported OK")
        except Exception as e:
            logs.append(f"Step 5 FAILED: Models import error: {str(e)}")
            logs.append(f"Step 5.1: Traceback: {traceback.format_exc()}")
            raise
        
        # Try importing database
        try:
            import database
            logs.append("Step 6: Database imported OK")
        except Exception as e:
            logs.append(f"Step 6 FAILED: Database import error: {str(e)}")
            logs.append(f"Step 6.1: Traceback: {traceback.format_exc()}")
            raise
        
        # Try importing main
        try:
            from main import app as main_app
            logs.append("Step 7: Main app imported OK")
            logs.append(f"Step 7.1: Main app routes = {[r.path for r in main_app.routes[:5]]}")
        except Exception as e:
            logs.append(f"Step 7 FAILED: Main app import error: {str(e)}")
            logs.append(f"Step 7.1: Traceback: {traceback.format_exc()}")
            raise
        
        logs.append("✅ SUCCESS: All imports completed!")
        
    except Exception as e:
        status = "error"
        error_detail = str(e)
        logs.append(f"❌ CRITICAL ERROR: {error_detail}")
    
    return JSONResponse(
        status_code=200 if status == "ok" else 500,
        content={
            "status": status,
            "error": error_detail,
            "logs": logs
        }
    )

# Vercel handler
handler = Mangum(app, lifespan="off")
