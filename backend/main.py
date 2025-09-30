import os
import sys
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import FastAPI and other dependencies after logging is configured
try:
    from fastapi import FastAPI, Depends, HTTPException, status, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import OAuth2PasswordBearer, HTTPBearer
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    
    # Import application components
    from app.core.config import settings
    from app.api.v1.api import api_router
    from app.core import security
    
    logger.info("Successfully imported all dependencies in main.py")
    
except ImportError as e:
    logger.error(f"Error importing application components in main.py: {e}")
    raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    logger.info(f"Environment: {settings.APP_ENV}")
    
    try:
        # Test database connection
        from app.core.supabase import supabase, test_connection
        if test_connection():
            logger.info("✅ Successfully connected to Supabase")
        else:
            raise Exception("Failed to connect to Supabase")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Bendine API",
    description="Backend API for Bendine Food and Beverage Management System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
cors_origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex="https://bendine.vercel.app",  # Allow all subdomains of vercel.app
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin"
    ],
    expose_headers=["Content-Disposition"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, 'headers') else None
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Debug endpoint to check environment variables
@app.get("/debug/env")
async def debug_env():
    return {
        "supabase_url_set": bool(settings.SUPABASE_URL),
        "supabase_key_set": bool(settings.SUPABASE_KEY),
        "app_env": settings.APP_ENV
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Annuti API",
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Test database connection
        from app.core.supabase import supabase
        result = supabase.client.table('users').select('*').limit(1).execute()
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
