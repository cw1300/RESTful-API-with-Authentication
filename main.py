"""
Main application entry point for the Task Management API.
This file initializes the FastAPI application and sets up all the necessary configurations.
Created by: [Your Name]
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routes import auth, tasks, users
from app.models import Base
from config.config import get_settings, engine

# Create the FastAPI application instance
app = FastAPI(
    title="Task Management API",
    description="A RESTful API for managing tasks with user authentication",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc"  # ReDoc documentation
)

# Initialize settings
settings = get_settings()

# Set up CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

# Create database tables
@app.on_event("startup")
async def startup_event():
    """
    Create all database tables on application startup.
    This ensures our database schema is ready before handling requests.
    """
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    """
    Root endpoint - returns a welcome message and API information.
    This helps users verify the API is running correctly.
    """
    return {
        "message": "Welcome to Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns the current status of the API.
    """
    return {"status": "healthy", "service": "Task Management API"}

if __name__ == "__main__":
    import uvicorn
    # Run the application with uvicorn when executed directly
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)