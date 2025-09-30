from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict, SecurityScopes
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
import logging
from typing import List, Optional

from app.core.config import settings
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    get_current_active_user,
    get_admin_user,
    get_manager_user,
    get_staff_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    oauth2_scheme
)
from app.core.supabase import supabase
from app.models.user import User, UserInDB, UserCreate, UserUpdate, Token, TokenData

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

router = APIRouter()

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email from Supabase Auth."""
    try:
        # Try to get user from auth.users
        auth_response = supabase.auth.admin.get_user_by_email(email)
        
        if not auth_response or not hasattr(auth_response, 'user') or not auth_response.user:
            logger.warning(f"No user found with email: {email}")
            return None
            
        auth_user = auth_response.user
        
        # Get additional user data from public.users if it exists
        try:
            result = supabase.client.table('users')\
                .select('*')\
                .eq('id', auth_user.id)\
                .single()\
                .execute()
            user_data = result.data or {}
        except Exception as db_error:
            logger.warning(f"Could not fetch user data from public.users: {db_error}")
            user_data = {}
        
        # Map auth user to our UserInDB model
        return UserInDB(
            id=auth_user.id,
            email=auth_user.email,
            hashed_password=auth_user.encrypted_password,
            full_name=user_data.get('full_name'),
            is_active=auth_user.confirmed_at is not None,
            is_superuser=user_data.get('is_superuser', False),
            role=user_data.get('role', 'user'),
            created_at=auth_user.created_at,
            updated_at=auth_user.updated_at or auth_user.created_at
        )
        
    except Exception as e:
        logger.error(f"Error in get_user_by_email for {email}: {str(e)}", exc_info=True)
        return None

@router.post("/login", response_model=Token, summary="OAuth2 compatible token login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    - **username**: Your email address
    - **password**: Your password
    
    Returns:
        - **access_token**: JWT token for authentication
        - **token_type**: Type of token (always "bearer")
    """
    try:
        email = form_data.username
        password = form_data.password
        
        logger.info(f"Login attempt for user: {email}")
        
        # Validate input
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        try:
            # Authenticate with Supabase
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                logger.warning(f"Authentication failed for {email}: Invalid credentials")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            user = auth_response.user
            logger.info(f"Supabase authentication successful for: {user.email}")
            
            # Get user details from database
            db_user = await get_user_by_email(user.email)
            if not db_user:
                # Create user in database if not exists
                logger.info(f"User {user.email} not found in database, creating...")
                db_user = UserInDB(
                    id=user.id,
                    email=user.email,
                    hashed_password=get_password_hash(password),
                    full_name=user.user_metadata.get('name', user.email.split('@')[0]),
                    is_active=True,
                    is_superuser=user.role == 'admin',
                    role=user.role or 'user',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                # Add to database
                user_data = db_user.dict(exclude={'hashed_password'})
                supabase.table('users').insert(user_data).execute()
            
            # Check if user is active
            if not db_user.is_active:
                logger.warning(f"Login failed - inactive user: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is inactive"
                )
            
            # Determine user's scopes based on role
            scopes = ["authenticated"]
            if db_user.role == "admin" or db_user.is_superuser:
                scopes.extend(["admin", "manager", "staff"])
            elif db_user.role == "manager":
                scopes.extend(["manager", "staff"])
            elif db_user.role == "staff":
                scopes.append("staff")
            
            # Create JWT token with appropriate scopes
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={
                    "sub": db_user.email,
                    "scopes": scopes,
                    "user_id": str(db_user.id),
                    "role": db_user.role
                },
                expires_delta=access_token_expires
            )
            
            logger.info(f"Login successful for user: {user.email}")
            return {
                "access_token": access_token, 
                "token_type": "bearer",
                "user": {
                    "email": db_user.email,
                    "full_name": db_user.full_name,
                    "role": db_user.role,
                    "is_superuser": db_user.is_superuser
                }
            }
            
        except HTTPException:
            raise
            
        except Exception as auth_error:
            logger.error(f"Authentication error for {email}: {str(auth_error)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again later."
        )

async def check_if_first_user() -> bool:
    """Check if there are any users in the database."""
    try:
        # Check auth.users
        auth_users = supabase.auth.admin.list_users()
        if auth_users.users and len(auth_users.users) > 1:  # >1 because we might be in the middle of registration
            return False
            
        # Also check public.users for consistency
        result = supabase.client.table('users').select('id', count='exact').execute()
        return result.count == 0
        
    except Exception as e:
        logger.error(f"Error checking for first user: {str(e)}")
        return False  # Default to False to be safe

@router.post(
    "/register", 
    response_model=User, 
    status_code=status.HTTP_201_CREATED, 
    summary="Register a new user"
)
async def register(user: UserCreate):
    """
    Register a new user.
    
    - **email**: Must be a valid email address
    - **password**: At least 8 characters
    - **full_name**: Optional full name
    
    The first user to register will be created as an admin. Subsequent users will be created as regular users.
    
    Returns:
        - The newly created user object (without password hash)
    """
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Check if user already exists
        try:
            existing_user = await get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        except Exception as e:
            logger.error(f"Error checking for existing user: {e}")
            raise
        
        # Check if this is the first user (should be an admin)
        is_first_user = await check_if_first_user()
        
        # Create user in Supabase Auth
        try:
            auth_response = supabase.auth.sign_up({
                "email": user.email,
                "password": user.password,
                "options": {
                    "data": {
                        "full_name": user.full_name,
                        "is_superuser": is_first_user,
                        "role": "admin" if is_first_user else "staff"
                    }
                }
            })
            logger.info(f"Supabase auth response: {auth_response}")
            
            if not auth_response.user:
                logger.error("Failed to create user in Supabase Auth")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user in authentication service"
                )
                
            # Create user in public.users table
            user_data = {
                "id": auth_response.user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": True,
                "is_superuser": is_first_user,
                "role": "admin" if is_first_user else "staff",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into public.users
            logger.info(f"Attempting to insert user data: {user_data}")
            result = supabase.client.table('users').insert(user_data).execute()
            logger.info(f"Database insert result: {result}")
            
            if not hasattr(result, 'data') or not result.data or len(result.data) == 0:
                logger.error("Failed to create user in database")
                # Try to clean up auth user if database insert fails
                try:
                    supabase.auth.admin.delete_user(auth_response.user.id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up auth user: {cleanup_error}")
                
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user in database"
                )
            
            # Return the created user (without sensitive data)
            created_user = result.data[0]
            created_user.pop("hashed_password", None)
            
            logger.info(f"User registered successfully: {user.email}")
            return created_user
            
        except HTTPException as http_exc:
            logger.warning(f"Registration failed for {user.email}: {http_exc.detail}")
            raise http_exc
            
        except Exception as e:
            logger.error(f"Error during registration for {user.email}: {str(e)}", exc_info=True)
            error_detail = f"Error during registration: {str(e)}"
            if hasattr(e, 'args') and e.args:
                error_detail = f"{error_detail} - Args: {e.args}"
            if hasattr(e, 'message'):
                error_detail = f"{error_detail} - Message: {e.message}"
                
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
            
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as they are
        logger.warning(f"Registration failed for {user.email}: {http_exc.detail}")
        raise http_exc
        
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Unexpected error during registration for {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )

@router.get("/test-token", response_model=User, summary="Test access token")
async def test_token(current_user: User = Depends(get_current_active_user)):
    """
    Test access token.
    
    This endpoint is used to test if the provided access token is valid.
    It returns the current user's information if the token is valid.
    
    Returns:
        - Current user's information
    """
    return current_user

@router.get(
    "/me", 
    response_model=User,
    summary="Get current user",
    response_description="The current user's information"
)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
    security_scopes: SecurityScopes = SecurityScopes(["authenticated"])
):
    """
    Get the currently authenticated user's information.
    
    This endpoint returns the details of the currently logged-in user
    based on the provided authentication token.
    
    Returns:
        - User: The current user's information
    """
    try:
        logger.info(f"Fetching current user: {current_user.email}")
        # Ensure we don't return sensitive data
        if hasattr(current_user, 'hashed_password'):
            current_user_dict = current_user.dict(exclude={"hashed_password"})
            return User(**current_user_dict)
        return current_user
    except Exception as e:
        logger.error(f"Error fetching current user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user information"
        )
