"""
Vercel Serverless Function Entry Point
This file adapts the FastAPI application for Vercel deployment
All code is now in api/ directory (no imports from backend/)
"""
from mangum import Mangum
from main import app

# Create Mangum handler for Vercel (disable lifespan for serverless)
handler = Mangum(app, lifespan="off")
