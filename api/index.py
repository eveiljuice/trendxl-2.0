"""
Vercel Serverless Function Entry Point
This file adapts the FastAPI application for Vercel deployment
"""
from main import app
from mangum import Mangum
import sys
import os

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Import mangum for AWS Lambda/Vercel adapter

# Import the FastAPI app

# Create Mangum handler for Vercel (disable lifespan for serverless)
handler = Mangum(app, lifespan="off")
