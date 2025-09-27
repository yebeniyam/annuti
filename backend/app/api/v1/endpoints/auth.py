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
from app.core.supabase import supabase, SupabaseClient
from app.models.user import User, UserInDB, UserCreate, UserUpdate, Token, TokenData

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

router = APIRouter()

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get a user by email from Supabase."""
    try:
        result = supabase.client.table('users').select('*').eq('email', email).single().execute()
        if result.data:
            return UserInDB(**result.data)
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

@router.post("/login", response_model=Token, summary="OAuth2 compatible token login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    scopes: SecurityScopes = SecurityScopes(["authenticated"])
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
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Get user from database
        user = get_user_by_email(form_data.username)
        
        if not user:
            logger.warning(f"Login failed - user not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Verify password
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Login failed - invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login failed - inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Determine user's scopes based on role
        scopes = ["authenticated"]
        if user.role == "admin":
            scopes.extend(["admin", "manager", "staff"])
        elif user.role == "manager":
            scopes.extend(["manager", "staff"])
        elif user.role == "staff":
            scopes.append("staff")
        
        # Create JWT token with appropriate scopes
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email},
            scopes=scopes,
            expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login for user {form_data.username}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login",
            headers={"WWW-Authenticate": "Bearer"},
        )

def check_if_first_user() -> bool:
    """Check if this is the first user in the database."""
    try:
        result = supabase.client.table('users').select('*').limit(1).execute()
        return not bool(result.data and len(result.data) > 0)
    except Exception as e:
        logger.error(f"Error checking for first user: {e}")
        return False

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
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if this is the first user (should be an admin)
        is_first_user = check_if_first_user()
        
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create user data for database
        user_data = user.dict(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        user_data["is_active"] = True
        user_data["is_superuser"] = is_first_user  # First user is superuser
        user_data["role"] = "admin" if is_first_user else "staff"  # First user is admin
        user_data["created_at"] = datetime.utcnow().isoformat()
        user_data["updated_at"] = datetime.utcnow().isoformat()
        
        logger.debug(f"Creating user with data: {user_data}")
        
        # Insert user into database
        try:
            result = supabase.client.table('users').insert(user_data).execute()
            
            # Check if the insert was successful
            if not result.data or len(result.data) == 0:
                logger.error(f"Failed to create user: No data returned from database")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user: No data returned from database"
                )
                
            # Get the created user
            created_user = result.data[0]
            
            # Remove sensitive data before returning
            created_user.pop("hashed_password", None)
            
            logger.info(f"User registered successfully: {user.email}")
            return created_user
            
        except Exception as db_error:
            logger.error(f"Database error during user registration: {db_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the user"
            )
        
    except HTTPException as http_exc:
        logger.warning(f"Registration failed for {user.email}: {http_exc.detail}")
        raise http_exc
        
    except Exception as e:
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
