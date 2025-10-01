"""
Vercel Serverless Function Entry Point
This file adapts the FastAPI application for Vercel deployment
"""
import sys
import os

# Add backend directory to Python path FIRST
backend_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'backend')
sys.path.insert(0, backend_path)

# Now import FastAPI app and Mangum
from mangum import Mangum
from main import app

# Create Mangum handler for Vercel (disable lifespan for serverless)
handler = Mangum(app, lifespan="off")
