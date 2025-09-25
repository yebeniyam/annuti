from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.menu import MenuItemCreate, MenuItemUpdate, MenuItem

router = APIRouter()

@router.get("/", response_model=List[MenuItem], summary="List menu items")
async def list_menu_items(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    current_user: MenuItem = Depends(get_current_active_user)
):
    """
    Retrieve a list of menu items.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **category_id**: Filter by category ID
    - **is_available**: Filter by availability status
    
    Returns:
        - List of menu item objects
    """
    try:
        # Build the query with joins to get category name
        query = supabase.client.table('menu_items').select(
            'id, name, description, price, cost, category_id, is_available, image_url, prep_time, is_featured, created_at, updated_at, menu_categories!inner(name)'
        )
        
        # Apply filters
        if category_id:
            query = query.eq('category_id', category_id)
        if is_available is not None:
            query = query.eq('is_available', is_available)
            
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Process the result to include category name
        items = []
        for item in result.data:
            # Extract category name from the joined data
            category_name = item.pop('menu_categories', {}).get('name', '')
            # Add category_name to the item object
            item['category_name'] = category_name
            items.append(MenuItem(**item))
        
        return items
    except Exception as e:
        print(f"Error retrieving menu items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menu items"
        )


@router.post("/", response_model=MenuItem, status_code=status.HTTP_201_CREATED, summary="Create a new menu item")
async def create_menu_item(
    item: MenuItemCreate,
    current_user: MenuItem = Depends(get_admin_user)
):
    """
    Create a new menu item.
    
    Only admins can create menu items.
    
    Parameters:
    - item: MenuItemCreate object containing the menu item information
    
    Returns:
        - MenuItem: The created menu item object
    """
    try:
        # Prepare menu item data for database
        item_data = item.dict()
        item_data['created_at'] = datetime.utcnow().isoformat()
        item_data['updated_at'] = item_data['created_at']
        item_data['is_available'] = item_data.get('is_available', True)
        
        # Insert new menu item into database
        result = supabase.client.table('menu_items').insert(item_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create menu item"
            )
        
        # Return the created menu item
        created_item = result.data[0]
        # Get category name for the response
        category_result = supabase.client.table('menu_categories').select('name').eq('id', created_item['category_id']).single().execute()
        created_item['category_name'] = category_result.data.get('name', '') if category_result.data else ''
        return MenuItem(**created_item)
    except Exception as e:
        print(f"Error creating menu item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating menu item"
        )


@router.get("/{item_id}", response_model=MenuItem, summary="Get menu item by ID")
async def get_menu_item(
    item_id: str,
    current_user: MenuItem = Depends(get_current_active_user)
):
    """
    Get a specific menu item by ID.
    
    Parameters:
    - item_id: ID of the menu item to retrieve
    
    Returns:
        - MenuItem: The requested menu item object
    """
    try:
        # Get item with category join
        result = supabase.client.table('menu_items').select(
            'id, name, description, price, cost, category_id, is_available, image_url, prep_time, is_featured, created_at, updated_at, menu_categories!inner(name)'
        ).eq('id', item_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Process the result to include category name
        item_data = result.data
        category_name = item_data.pop('menu_categories', {}).get('name', '')
        item_data['category_name'] = category_name
        return MenuItem(**item_data)
    except Exception as e:
        print(f"Error retrieving menu item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menu item"
        )


@router.put("/{item_id}", response_model=MenuItem, summary="Update a menu item")
async def update_menu_item(
    item_id: str,
    item_update: MenuItemUpdate,
    current_user: MenuItem = Depends(get_admin_user)
):
    """
    Update a menu item.
    
    Only admins can update menu items.
    
    Parameters:
    - item_id: ID of the menu item to update
    - item_update: MenuItemUpdate object containing the fields to update
    
    Returns:
        - MenuItem: The updated menu item object
    """
    try:
        # Get current item to check if it exists
        current_item_result = supabase.client.table('menu_items').select('*').eq('id', item_id).single().execute()
        
        if not current_item_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Prepare update data
        update_data = item_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update the menu item in database
        result = supabase.client.table('menu_items').update(update_data).eq('id', item_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Return the updated menu item
        updated_item = result.data[0]
        # Get category name for the response
        category_result = supabase.client.table('menu_categories').select('name').eq('id', updated_item['category_id']).single().execute()
        updated_item['category_name'] = category_result.data.get('name', '') if category_result.data else ''
        return MenuItem(**updated_item)
    except Exception as e:
        print(f"Error updating menu item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating menu item"
        )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a menu item")
async def delete_menu_item(
    item_id: str,
    current_user: MenuItem = Depends(get_admin_user)
):
    """
    Delete a menu item.
    
    Only admins can delete menu items.
    
    Parameters:
    - item_id: ID of the menu item to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if menu item exists
        current_item_result = supabase.client.table('menu_items').select('*').eq('id', item_id).single().execute()
        
        if not current_item_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # For soft delete, update the is_available field to false
        result = supabase.client.table('menu_items').update({
            'is_available': False,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', item_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting menu item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting menu item"
        )