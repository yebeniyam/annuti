import os
import sys
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
from app.core.security import get_password_hash, verify_password

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
            
            # Ensure admin user exists
            admin_email = "admin@example.com"
            # Use a strong password that's within bcrypt's 72-byte limit
            admin_password = "Admin@Secure123!"
            admin_name = "Admin"
            
            try:
                # Check if admin user exists
                result = supabase.from_('users').select('*').eq('email', admin_email).execute()
                
                if not result.data:
                    # Create admin user if not exists
                    hashed_password = get_password_hash(admin_password)
                    
                    # Create auth user
                    auth_response = supabase.auth.admin.create_user({
                        "email": admin_email,
                        "password": admin_password,
                        "email_confirm": True,
                        "user_metadata": {
                            "name": admin_name
                        }
                    })
                    
                    if not auth_response.user:
                        raise Exception("Failed to create auth user")
                    
                    # Create user in public.users
                    user_data = {
                        "id": str(auth_response.user.id),
                        "email": admin_email,
                        "full_name": admin_name,
                        "hashed_password": hashed_password,
                        "is_active": True,
                        "is_superuser": True,
                        "role": "admin"
                    }
                    
                    result = supabase.from_('users').insert(user_data).execute()
                    if hasattr(result, 'error') and result.error:
                        raise Exception(f"Failed to create admin user: {result.error}")
                    
                    logger.info("✅ Admin user created successfully")
                else:
                    # Update admin user password and details to ensure they're set correctly
                    try:
                        admin_user = result.data[0]
                        user_id = admin_user['id']
                        
                        # Update auth user password and details
                        supabase.auth.admin.update_user_by_id(
                            str(user_id),
                            {
                                "password": admin_password,
                                "email": admin_email,
                                "user_metadata": {"name": admin_name}
                            }
                        )
                        
                        # Update user in public.users
                        update_data = {
                            "email": admin_email,
                            "full_name": admin_name,
                            "is_active": True,
                            "is_superuser": True,
                            "role": "admin"
                        }
                        
                        # Only update hashed password if it's different or missing
                        hashed_password = admin_user.get('hashed_password')
                        if not hashed_password or not verify_password(admin_password, hashed_password):
                            update_data["hashed_password"] = get_password_hash(admin_password)
                        
                        update_result = supabase.from_('users').update(update_data).eq('id', user_id).execute()
                        
                        if hasattr(update_result, 'error') and update_result.error:
                            logger.warning(f"⚠️ Failed to update admin user details: {update_result.error}")
                        else:
                            logger.info("✅ Admin user details updated successfully")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to update admin user: {e}")
                    
                    logger.info("✅ Admin user already exists")
                    
            except Exception as e:
                logger.error(f"❌ Failed to ensure admin user exists: {e}")
                
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
