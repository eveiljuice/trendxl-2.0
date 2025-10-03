"""
Vercel Serverless Function Entry Point
FastAPI ASGI application for Vercel
"""
import sys
import os

# Add the current directory to Python path for module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the FastAPI app
# Vercel will automatically detect and handle the ASGI application
from main import app
