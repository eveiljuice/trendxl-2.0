#!/usr/bin/env python3
"""
TrendXL 2.0 Backend Server Runner
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import settings

def main():
    """Run the FastAPI server"""
    print("🚀 Starting TrendXL 2.0 Backend Server...")
    print(f"📍 Host: {settings.host}")
    print(f"🔌 Port: {settings.port}")
    print(f"🐛 Debug: {settings.debug}")
    print(f"📋 Redis: {settings.redis_url}")
    print("-" * 50)
    
    # Check environment variables
    required_vars = ["ENSEMBLE_API_TOKEN", "OPENAI_API_KEY"]
    missing_vars = []

    # Settings already imported above
    
    # Check actual values from settings
    ensemble_token = settings.ensemble_api_token if hasattr(settings, 'ensemble_api_token') else os.getenv("ENSEMBLE_API_TOKEN")
    openai_key = settings.openai_api_key if hasattr(settings, 'openai_api_key') else os.getenv("OPENAI_API_KEY")
    
    print(f"🔑 Loaded ENSEMBLE_API_TOKEN: {'✅ Found' if ensemble_token else '❌ Missing'}")
    print(f"🔑 Loaded OPENAI_API_KEY: {'✅ Found' if openai_key else '❌ Missing'}")
    
    if not ensemble_token or ensemble_token in ["", "your_ensemble_data_token_here"]:
        missing_vars.append("ENSEMBLE_API_TOKEN")
    if not openai_key or openai_key in ["", "your_openai_api_key_here"]:
        missing_vars.append("OPENAI_API_KEY")

    if missing_vars:
        print("⚠️  Missing or placeholder API keys:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these variables in your .env file with real API keys")
        print("   Server will start but API calls will fail without valid keys")
        
        # In production, don't wait - just start
        # In development, give user time to cancel
        if settings.debug:
            print("   Press Ctrl+C to exit and add keys, or continue for demo mode...")
            try:
                import time
                for i in range(5, 0, -1):
                    print(f"   Continuing in {i} seconds...")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Exiting. Please add API keys to .env file.")
                sys.exit(1)
        else:
            print("   ⚠️  Production mode: Starting immediately without valid keys")
    else:
        print("✅ All API keys configured")
    
    # Start server
    try:
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info" if settings.debug else "warning",
            access_log=settings.debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
