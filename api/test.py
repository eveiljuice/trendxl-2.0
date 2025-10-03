"""
Minimal FastAPI test for Vercel
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/test")
def test():
    return {
        "status": "ok", 
        "message": "Minimal Python FastAPI handler works on Vercel!"
    }

# Vercel handler
handler = Mangum(app, lifespan="off")
