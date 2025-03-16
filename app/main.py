"""
Main application module.

This module initializes and configures the FastAPI application.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.models import model_trainer

# Initialize FastAPI app
app = FastAPI(
    title="CV Parser API",
    description="API for parsing and anonymizing CVs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    # Create saved_models directory if it doesn't exist
    os.makedirs("app/models/saved_models", exist_ok=True)
    
    # Initialize models
    try:
        # Train models if they don't exist
        model_trainer.train_models(force_retrain=False)
    except Exception as e:
        print(f"Error initializing models: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 