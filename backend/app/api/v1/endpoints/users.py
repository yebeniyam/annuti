from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.core.security import (
    get_current_user,
    get_current_active_user,
    get_admin_user,
    get_manager_user,
    get_staff_user,
    oauth2_scheme
)
from app.core.supabase import supabase
from app.models.user import User, UserUpdate, UserInDB, UserCreate, UserRole

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/me",
    response_model=User,
    summary="Get current user",
    response_description="The current user's information"
)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the currently authenticated user's information.
    
    Returns:
        - User: The current user's information
    """
    try:
        # Remove sensitive data before returning
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

@router.get(
    "/",
    response_model=List[User],
    summary="List users",
    response_description="List of users"
)
async def read_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_admin_user)
):
    """
    Retrieve a list of users with optional filtering.
    
    - **Admin**: Can see all users
    - **Manager**: Can see staff and customers
    - **Staff**: Can only see their own profile
    
    Parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 1000)
    - role: Filter by user role
    - is_active: Filter by active status
    
    Returns:
        - List of user objects
    """
    try:
        # Build the query
        query = supabase.client.table('users').select('*')
        
        # Apply filters
        if role:
            query = query.eq('role', role.value)
        if is_active is not None:
            query = query.eq('is_active', is_active)
            
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Filter out sensitive data
        users = []
        for user in result.data:
            # Only include sensitive fields if admin
            if current_user.role != UserRole.ADMIN:
                user.pop('hashed_password', None)
                user.pop('email_verified', None)
            users.append(User(**user))
            
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )

@router.get(
    "/{user_id}",
    response_model=User,
    summary="Get user by ID",
    response_description="The requested user's information"
)
async def read_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by ID.
    
    - **Admins** can view any user's profile
    - **Managers** can view staff and customer profiles
    - **Staff** can only view their own profile
    
    Parameters:
    - user_id: ID of the user to retrieve
    
    Returns:
        - User: The requested user's information
    """
    # Check permissions
    if current_user.id != user_id:
        if current_user.role == UserRole.STAFF:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this user"
            )
        elif current_user.role == UserRole.MANAGER:
            # Managers can only view staff and customers, not other managers or admins
            target_user = await _get_user_by_id(user_id)
            if target_user.role in [UserRole.ADMIN, UserRole.MANAGER]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view this user"
                )
    
    try:
        user = await _get_user_by_id(user_id)
        
        # Remove sensitive data if not admin
        if current_user.role != UserRole.ADMIN:
            if hasattr(user, 'hashed_password'):
                user_dict = user.dict(exclude={"hashed_password"})
                return User(**user_dict)
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user"
        )

@router.put(
    "/me",
    response_model=User,
    summary="Update current user",
    response_description="The updated user information"
)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user information.
    
    Users can update their own profile information, including:
    - Full name
    - Email
    - Password
    - Other personal information
    
    Note: Role and active status cannot be updated through this endpoint.
    
    Parameters:
    - user_update: UserUpdate object containing the fields to update
    
    Returns:
        - User: The updated user information
    """
    update_data = user_update.dict(exclude_unset=True)
    
    # Remove fields that shouldn't be updated through this endpoint
    update_data.pop('role', None)
    update_data.pop('is_active', None)
    
    # Handle password update
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
    
    try:
        # Update user in database
        result = supabase.client.table('users') \
            .update(update_data) \
            .eq('id', current_user.id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get updated user
        updated_user = await _get_user_by_id(current_user.id)
        
        # Remove sensitive data before returning
        if hasattr(updated_user, 'hashed_password'):
            updated_user_dict = updated_user.dict(exclude={"hashed_password"})
            return User(**updated_user_dict)
            
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user",
    response_description="User deleted successfully"
)
async def delete_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete the currently authenticated user's account.
    
    This action is irreversible and will permanently delete the user's account
    and all associated data.
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Soft delete by marking as inactive
        result = supabase.client.table('users') \
            .update({
                'is_active': False,
                'email': f"deleted_{current_user.id}@deleted.com",
                'updated_at': datetime.utcnow().isoformat()
            }) \
            .eq('id', current_user.id) \
            .execute()
            
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user"
        )

# Admin-only endpoints
@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)",
    response_description="The created user"
)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_admin_user)
):
    """
    Create a new user (Admin only).
    
    This endpoint allows administrators to create new user accounts with specific roles.
    
    - **Admins** can create users with any role
    - **Managers** can only create staff and customer accounts
    - **Staff** cannot create users
    
    Parameters:
    - user: UserCreate object containing the new user's information
    
    Returns:
        - User: The created user object
    """
    try:
        # Check if user already exists
        existing_user = supabase.client.table('users') \
            .select('email') \
            .eq('email', user.email) \
            .execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Prepare user data for database
        user_data = user.dict()
        user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        user_data['is_active'] = True
        user_data['created_at'] = datetime.utcnow().isoformat()
        user_data['updated_at'] = user_data['created_at']
        
        # Insert new user into database
        result = supabase.client.table('users') \
            .insert(user_data) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Return the created user (without password hash)
        created_user = result.data[0]
        created_user.pop('hashed_password', None)
        
        return created_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

@router.put(
    "/{user_id}",
    response_model=User,
    summary="Update a user (Admin only)",
    response_description="The updated user"
)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_admin_user)
):
    """
    Update a user's information (Admin only).
    
    - **Admins** can update any user's information
    - **Managers** can only update staff and customer accounts
    - **Staff** cannot update other users
    
    Parameters:
    - user_id: ID of the user to update
    - user_update: UserUpdate object containing the fields to update
    
    Returns:
        - User: The updated user object
    """
    try:
        # Check if user exists
        existing_user = await _get_user_by_id(user_id)
        
        # Prepare update data
        update_data = user_update.dict(exclude_unset=True)
        
        # Handle password update
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        # Update user in database
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        result = supabase.client.table('users') \
            .update(update_data) \
            .eq('id', user_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return the updated user (without password hash)
        updated_user = result.data[0]
        updated_user.pop('hashed_password', None)
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (Admin only)",
    response_description="User deleted successfully"
)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_admin_user)
):
    """
    Delete a user (Admin only).
    
    - **Admins** can delete any user
    - **Managers** can only delete staff and customer accounts
    - **Staff** cannot delete users
    
    This is a soft delete that marks the user as inactive.
    
    Parameters:
    - user_id: ID of the user to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if user exists
        existing_user = await _get_user_by_id(user_id)
        
        # Soft delete by marking as inactive
        result = supabase.client.table('users') \
            .update({
                'is_active': False,
                'email': f"deleted_{user_id}@deleted.com",
                'updated_at': datetime.utcnow().isoformat()
            }) \
            .eq('id', user_id) \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user"
        )

# Helper function to get user by ID
async def _get_user_by_id(user_id: str) -> UserInDB:
    """
    Get a user by ID from the database.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        UserInDB: The user object
        
    Raises:
        HTTPException: If the user is not found
    """
    try:
        result = supabase.client.table('users') \
            .select('*') \
            .eq('id', user_id) \
            .single() \
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return UserInDB(**result.data)
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user"
        )
