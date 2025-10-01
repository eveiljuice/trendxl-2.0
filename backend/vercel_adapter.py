"""
Vercel Adapter for FastAPI Application
Handles the conversion between Vercel's serverless format and FastAPI
"""
from mangum import Mangum
from main import app

# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
