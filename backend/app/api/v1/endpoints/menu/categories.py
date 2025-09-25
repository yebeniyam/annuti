from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.menu import MenuCategoryCreate, MenuCategoryUpdate, MenuCategory

router = APIRouter()

@router.get("/", response_model=List[MenuCategory], summary="List menu categories")
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: MenuCategory = Depends(get_current_active_user)
):
    """
    Retrieve a list of menu categories.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **is_active**: Filter by active status
    
    Returns:
        - List of menu category objects
    """
    try:
        # Build the query
        query = supabase.client.table('menu_categories').select('*')
        
        # Apply filters
        if is_active is not None:
            query = query.eq('is_active', is_active)
            
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        categories = [MenuCategory(**category) for category in result.data]
        
        return categories
    except Exception as e:
        print(f"Error retrieving categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving categories"
        )


@router.post("/", response_model=MenuCategory, status_code=status.HTTP_201_CREATED, summary="Create a new menu category")
async def create_category(
    category: MenuCategoryCreate,
    current_user: MenuCategory = Depends(get_admin_user)
):
    """
    Create a new menu category.
    
    Only admins can create menu categories.
    
    Parameters:
    - category: MenuCategoryCreate object containing the category information
    
    Returns:
        - MenuCategory: The created category object
    """
    try:
        # Prepare category data for database
        category_data = category.dict()
        category_data['created_at'] = datetime.utcnow().isoformat()
        category_data['updated_at'] = category_data['created_at']
        category_data['is_active'] = category_data.get('is_active', True)
        
        # Insert new category into database
        result = supabase.client.table('menu_categories').insert(category_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create category"
            )
        
        # Return the created category
        created_category = result.data[0]
        return MenuCategory(**created_category)
    except Exception as e:
        print(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating category"
        )


@router.get("/{category_id}", response_model=MenuCategory, summary="Get category by ID")
async def get_category(
    category_id: str,
    current_user: MenuCategory = Depends(get_current_active_user)
):
    """
    Get a specific menu category by ID.
    
    Parameters:
    - category_id: ID of the category to retrieve
    
    Returns:
        - MenuCategory: The requested category object
    """
    try:
        result = supabase.client.table('menu_categories').select('*').eq('id', category_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return MenuCategory(**result.data)
    except Exception as e:
        print(f"Error retrieving category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving category"
        )


@router.put("/{category_id}", response_model=MenuCategory, summary="Update a menu category")
async def update_category(
    category_id: str,
    category_update: MenuCategoryUpdate,
    current_user: MenuCategory = Depends(get_admin_user)
):
    """
    Update a menu category.
    
    Only admins can update menu categories.
    
    Parameters:
    - category_id: ID of the category to update
    - category_update: MenuCategoryUpdate object containing the fields to update
    
    Returns:
        - MenuCategory: The updated category object
    """
    try:
        # Get current category to check if it exists
        current_category_result = supabase.client.table('menu_categories').select('*').eq('id', category_id).single().execute()
        
        if not current_category_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Prepare update data
        update_data = category_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update the category in database
        result = supabase.client.table('menu_categories').update(update_data).eq('id', category_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Return the updated category
        updated_category = result.data[0]
        return MenuCategory(**updated_category)
    except Exception as e:
        print(f"Error updating category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating category"
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a menu category")
async def delete_category(
    category_id: str,
    current_user: MenuCategory = Depends(get_admin_user)
):
    """
    Delete a menu category.
    
    Only admins can delete menu categories.
    
    Parameters:
    - category_id: ID of the category to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if category exists
        current_category_result = supabase.client.table('menu_categories').select('*').eq('id', category_id).single().execute()
        
        if not current_category_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # For soft delete, update the is_active field
        result = supabase.client.table('menu_categories').update({
            'is_active': False,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', category_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting category"
        )