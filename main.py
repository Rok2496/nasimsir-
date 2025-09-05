from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import shutil
import uuid
from pathlib import Path

from database import engine
from models import Base
from routes import (
    product_router,
    order_router,
    chat_router,
    admin_router,
    dashboard_router,
    files_router
)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="SmartTech E-commerce API",
    description="API for SmartTech Interactive Smart Board E-commerce Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - more restrictive for production
if os.getenv("RENDER"):
    # For Render deployment, allow specific origins
    allowed_origins = [
        "https://your-frontend-domain.onrender.com",  # Replace with your frontend URL
        "https://your-custom-domain.com",  # Replace with your custom domain
        "https://smarttech1.netlify.app",  # Your production frontend
        "http://localhost:3000",  # For local development
        "http://localhost:3001"   # For local development
    ]
else:
    # For local development, allow all origins
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(product_router)
app.include_router(order_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(dashboard_router)
app.include_router(files_router)

# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to SmartTech E-commerce API",
        "product": "Interactive Smart Board RK3588",
        "features": [
            "Android 12",
            "16GB RAM + 256GB Storage",
            "48MP AI Camera",
            "8 Microphones",
            "NFC Support",
            "Fingerprint Scanner",
            "2.1 Channel Audio"
        ],
        "contact": "01678-134547",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SmartTech E-commerce API"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    # Check if we're running on Render
    if os.getenv("RENDER"):
        # Render will set the PORT environment variable
        port = int(os.environ.get("PORT", 8000))
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    else:
        # Local development
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )