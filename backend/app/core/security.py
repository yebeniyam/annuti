import logging
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union

__all__ = [
    'oauth2_scheme',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'get_current_user',
    'get_current_active_user',
    'get_admin_user',
    'get_manager_user',
    'get_staff_user',
    'ACCESS_TOKEN_EXPIRE_MINUTES'
]

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    # Import required modules after logging is configured
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from fastapi import Depends, HTTPException, status, Security
    from fastapi.security import OAuth2PasswordBearer, SecurityScopes
    from pydantic import ValidationError, BaseModel
    
    # Import app-specific modules
    from app.core.config import settings
    from app.models.user import UserInDB, TokenData, UserRole, User
    
    logger.info("Successfully imported all dependencies in security.py")
    
except ImportError as e:
    logger.error(f"Error importing dependencies in security.py: {e}")
    raise

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class TokenPayload(BaseModel):
    sub: str
    scopes: List[str] = []
    exp: int

# Define the security scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scopes={
        "admin": "Admin access",
        "manager": "Manager access",
        "staff": "Staff access",
        "customer": "Customer access"
    }
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Generate a password hash.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error hashing password"
        )

def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[List[str]] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Add scopes to the token
    if scopes is None:
        scopes = ["authenticated"]
    
    to_encode.update({
        "exp": expire,
        "scopes": scopes
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Get token scopes
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(
            username=username,
            scopes=token_scopes
        )
        
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    try:
        # Get user from database
        result = supabase.client.table('users') \
            .select('*') \
            .eq('email', token_data.username) \
            .single() \
            .execute()
        
        if not result.data:
            logger.warning(f"User not found: {token_data.username}")
            raise credentials_exception
            
        # Create UserInDB instance
        user_data = result.data
        return UserInDB(**user_data)
        
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error getting user from database: {e}")
        raise credentials_exception

# Dependency for getting the current active user
get_current_active_user = get_current_user

# Role-based dependencies
def get_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency to get the current admin user.
    Raises HTTP 403 if the user is not an admin.
    """
    if UserRole.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required."
        )
    return current_user

def get_manager_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency to get the current manager user.
    Raises HTTP 403 if the user is not at least a manager.
    """
    if not any(role in current_user.roles for role in [UserRole.ADMIN, UserRole.MANAGER]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Manager or higher access required."
        )
    return current_user

def get_staff_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency to get the current staff user.
    Raises HTTP 403 if the user is not at least a staff member.
    """
    if not any(role in current_user.roles for role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.STAFF]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Staff or higher access required."
        )
    return current_user
