"""
Main FastAPI application for the Voice Agent.
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.api import api_router
from src.utils.logging import setup_logging
from src import __version__

# Set up logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Voice Interview Agent",
    description="API for real-time voice interview agent with Edge TTS",
    version=__version__
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": __version__
    }

# Root redirect to docs
@app.get("/")
async def root():
    """Redirect to API documentation"""
    return {"message": "Welcome to the Voice Interview Agent API", "docs_url": "/docs"}

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Run the application
    logger.info(f"Starting server on port {port}")
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True) 