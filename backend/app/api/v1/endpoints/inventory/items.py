from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.inventory import (
    IngredientCreate, IngredientUpdate, Ingredient,
    UnitCreate, UnitUpdate, Unit,
    InventoryTransactionCreate, InventoryTransactionUpdate, InventoryTransaction,
    InventoryTransactionItemCreate, InventoryTransactionItemUpdate, InventoryTransactionItem
)

router = APIRouter()

# Ingredients endpoints
@router.get("/ingredients", response_model=List[Ingredient], summary="List ingredients")
async def list_ingredients(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    low_stock: Optional[bool] = Query(None, description="Filter by low stock status"),
    current_user: Ingredient = Depends(get_current_active_user)
):
    """
    Retrieve a list of ingredients.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 1000)
    - **category**: Filter by category
    - **low_stock**: Filter by low stock status
    
    Returns:
        - List of ingredient objects
    """
    try:
        # Build the query
        query = supabase.client.table('ingredients').select('*')
        
        # Apply filters
        if category:
            query = query.eq('category', category)
        if low_stock is not None:
            if low_stock:
                # Filter for ingredients where current_stock <= min_stock
                query = query.lte('current_stock', supabase.client.from_('ingredients').select('min_stock').eq('id', 'ingredients.id'))
            else:
                query = query.gt('current_stock', 'min_stock')  # This is a simplified approach
                
        # A better approach for low stock filtering would be to use a computed column
        if low_stock:
            # We'll handle this in application logic after fetching
            pass
            
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        ingredients = [Ingredient(**ingredient) for ingredient in result.data]
        
        # Additional filtering for low stock if needed
        if low_stock is not None:
            if low_stock:
                ingredients = [i for i in ingredients if i.current_stock <= i.min_stock]
            else:
                ingredients = [i for i in ingredients if i.current_stock > i.min_stock]
        
        return ingredients
    except Exception as e:
        print(f"Error retrieving ingredients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving ingredients"
        )


@router.post("/ingredients", response_model=Ingredient, status_code=status.HTTP_201_CREATED, summary="Create a new ingredient")
async def create_ingredient(
    ingredient: IngredientCreate,
    current_user: Ingredient = Depends(get_admin_user)
):
    """
    Create a new ingredient.
    
    Only admins can create ingredients.
    
    Parameters:
    - ingredient: IngredientCreate object containing the ingredient information
    
    Returns:
        - Ingredient: The created ingredient object
    """
    try:
        # Prepare ingredient data for database
        ingredient_data = ingredient.dict()
        ingredient_data['created_at'] = datetime.utcnow().isoformat()
        ingredient_data['updated_at'] = ingredient_data['created_at']
        
        # Insert new ingredient into database
        result = supabase.client.table('ingredients').insert(ingredient_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create ingredient"
            )
        
        # Return the created ingredient
        created_ingredient = result.data[0]
        return Ingredient(**created_ingredient)
    except Exception as e:
        print(f"Error creating ingredient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating ingredient"
        )


@router.get("/ingredients/{ingredient_id}", response_model=Ingredient, summary="Get ingredient by ID")
async def get_ingredient(
    ingredient_id: str,
    current_user: Ingredient = Depends(get_current_active_user)
):
    """
    Get a specific ingredient by ID.
    
    Parameters:
    - ingredient_id: ID of the ingredient to retrieve
    
    Returns:
        - Ingredient: The requested ingredient object
    """
    try:
        result = supabase.client.table('ingredients').select('*').eq('id', ingredient_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        
        return Ingredient(**result.data)
    except Exception as e:
        print(f"Error retrieving ingredient {ingredient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving ingredient"
        )


@router.put("/ingredients/{ingredient_id}", response_model=Ingredient, summary="Update an ingredient")
async def update_ingredient(
    ingredient_id: str,
    ingredient_update: IngredientUpdate,
    current_user: Ingredient = Depends(get_admin_user)
):
    """
    Update an ingredient.
    
    Only admins can update ingredients.
    
    Parameters:
    - ingredient_id: ID of the ingredient to update
    - ingredient_update: IngredientUpdate object containing the fields to update
    
    Returns:
        - Ingredient: The updated ingredient object
    """
    try:
        # Get current ingredient to check if it exists
        current_ingredient_result = supabase.client.table('ingredients').select('*').eq('id', ingredient_id).single().execute()
        
        if not current_ingredient_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        
        # Prepare update data
        update_data = ingredient_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update the ingredient in database
        result = supabase.client.table('ingredients').update(update_data).eq('id', ingredient_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        
        # Return the updated ingredient
        updated_ingredient = result.data[0]
        return Ingredient(**updated_ingredient)
    except Exception as e:
        print(f"Error updating ingredient {ingredient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating ingredient"
        )


@router.delete("/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an ingredient")
async def delete_ingredient(
    ingredient_id: str,
    current_user: Ingredient = Depends(get_admin_user)
):
    """
    Delete an ingredient.
    
    Only admins can delete ingredients.
    
    Parameters:
    - ingredient_id: ID of the ingredient to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if ingredient exists
        current_ingredient_result = supabase.client.table('ingredients').select('*').eq('id', ingredient_id).single().execute()
        
        if not current_ingredient_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
        
        # For soft delete, update the is_available field to false
        # (Assuming we have an is_active or is_available field)
        # If not, we might need to implement true deletion or mark for deletion
        result = supabase.client.table('ingredients').update({
            'is_active': False,  # assuming there's an is_active field
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', ingredient_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingredient not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting ingredient {ingredient_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting ingredient"
        )


# Units endpoints
@router.get("/units", response_model=List[Unit], summary="List units")
async def list_units(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of records to return"),
    current_user: Unit = Depends(get_current_active_user)
):
    """
    Retrieve a list of units.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return (max 1000)
    
    Returns:
        - List of unit objects
    """
    try:
        # Build the query
        query = supabase.client.table('units').select('*')
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        units = [Unit(**unit) for unit in result.data]
        
        return units
    except Exception as e:
        print(f"Error retrieving units: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving units"
        )


@router.post("/units", response_model=Unit, status_code=status.HTTP_201_CREATED, summary="Create a new unit")
async def create_unit(
    unit: UnitCreate,
    current_user: Unit = Depends(get_admin_user)
):
    """
    Create a new unit.
    
    Only admins can create units.
    
    Parameters:
    - unit: UnitCreate object containing the unit information
    
    Returns:
        - Unit: The created unit object
    """
    try:
        # Prepare unit data for database
        unit_data = unit.dict()
        unit_data['created_at'] = datetime.utcnow().isoformat()
        unit_data['updated_at'] = unit_data['created_at']
        
        # Insert new unit into database
        result = supabase.client.table('units').insert(unit_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create unit"
            )
        
        # Return the created unit
        created_unit = result.data[0]
        return Unit(**created_unit)
    except Exception as e:
        print(f"Error creating unit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating unit"
        )


@router.get("/units/{unit_id}", response_model=Unit, summary="Get unit by ID")
async def get_unit(
    unit_id: str,
    current_user: Unit = Depends(get_current_active_user)
):
    """
    Get a specific unit by ID.
    
    Parameters:
    - unit_id: ID of the unit to retrieve
    
    Returns:
        - Unit: The requested unit object
    """
    try:
        result = supabase.client.table('units').select('*').eq('id', unit_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        
        return Unit(**result.data)
    except Exception as e:
        print(f"Error retrieving unit {unit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving unit"
        )


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a unit")
async def delete_unit(
    unit_id: str,
    current_user: Unit = Depends(get_admin_user)
):
    """
    Delete a unit.
    
    Only admins can delete units.
    
    Parameters:
    - unit_id: ID of the unit to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if unit exists
        current_unit_result = supabase.client.table('units').select('*').eq('id', unit_id).single().execute()
        
        if not current_unit_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        
        # Check if the unit is being used by any ingredients
        ingredients_result = supabase.client.table('ingredients').select('id').eq('unit', current_unit_result.data['abbreviation']).execute()
        if ingredients_result.data and len(ingredients_result.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete unit: it is being used by one or more ingredients"
            )
        
        # Delete the unit
        result = supabase.client.table('units').delete().eq('id', unit_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting unit {unit_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting unit"
        )