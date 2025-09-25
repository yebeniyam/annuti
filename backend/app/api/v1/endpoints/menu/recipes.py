from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.menu import RecipeCreate, RecipeUpdate, Recipe, RecipeIngredientCreate, RecipeIngredientUpdate, RecipeIngredient

router = APIRouter()

@router.get("/{item_id}/recipe", response_model=Recipe, summary="Get recipe for menu item")
async def get_recipe(
    item_id: str,
    current_user: Recipe = Depends(get_current_active_user)
):
    """
    Get the recipe for a specific menu item.
    
    Parameters:
    - item_id: ID of the menu item
    
    Returns:
        - Recipe: The recipe object for the menu item
    """
    try:
        # Get the recipe for the menu item
        result = supabase.client.table('recipes').select('*').eq('menu_item_id', item_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found for this menu item"
            )
        
        recipe = Recipe(**result.data)
        
        # Get recipe ingredients
        ingredients_result = supabase.client.table('recipe_ingredients').select('*').eq('recipe_id', recipe.id).execute()
        recipe.ingredients = [RecipeIngredient(**ingredient) for ingredient in ingredients_result.data]
        
        return recipe
    except Exception as e:
        print(f"Error retrieving recipe for menu item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving recipe"
        )


@router.put("/{item_id}/recipe", response_model=Recipe, summary="Update recipe for menu item")
async def update_recipe(
    item_id: str,
    recipe_update: RecipeUpdate,
    current_user: Recipe = Depends(get_admin_user)
):
    """
    Update the recipe for a menu item.
    
    Only admins can update recipes.
    
    Parameters:
    - item_id: ID of the menu item
    - recipe_update: RecipeUpdate object containing the recipe information
    
    Returns:
        - Recipe: The updated recipe object
    """
    try:
        # Check if menu item exists
        menu_item_result = supabase.client.table('menu_items').select('id').eq('id', item_id).single().execute()
        if not menu_item_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        # Check if recipe exists for this menu item
        recipe_result = supabase.client.table('recipes').select('id').eq('menu_item_id', item_id).single().execute()
        
        recipe_id = None
        if recipe_result.data:
            # Recipe exists, update it
            recipe_id = recipe_result.data['id']
            update_data = recipe_update.dict(exclude_unset=True)
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            supabase.client.table('recipes').update(update_data).eq('id', recipe_id).execute()
        else:
            # Recipe doesn't exist, create it
            recipe_data = recipe_update.dict()
            recipe_data['menu_item_id'] = item_id
            recipe_data['created_at'] = datetime.utcnow().isoformat()
            recipe_data['updated_at'] = recipe_data['created_at']
            
            create_result = supabase.client.table('recipes').insert(recipe_data).execute()
            if not create_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create recipe"
                )
            recipe_id = create_result.data[0]['id']
        
        if not recipe_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create or update recipe"
            )
        
        # Update recipe ingredients if provided
        if hasattr(recipe_update, 'ingredients') and recipe_update.ingredients is not None:
            # First, delete existing ingredients for this recipe
            supabase.client.table('recipe_ingredients').delete().eq('recipe_id', recipe_id).execute()
            
            # Then add the new ingredients
            for ingredient_data in recipe_update.ingredients:
                ingredient_dict = ingredient_data.dict()
                ingredient_dict['recipe_id'] = recipe_id
                supabase.client.table('recipe_ingredients').insert(ingredient_dict).execute()
        
        # Return the updated recipe
        final_recipe_result = supabase.client.table('recipes').select('*').eq('id', recipe_id).single().execute()
        if not final_recipe_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found after update"
            )
        
        recipe = Recipe(**final_recipe_result.data)
        
        # Get updated recipe ingredients
        ingredients_result = supabase.client.table('recipe_ingredients').select('*').eq('recipe_id', recipe.id).execute()
        recipe.ingredients = [RecipeIngredient(**ingredient) for ingredient in ingredients_result.data] if ingredients_result.data else []
        
        return recipe
    except Exception as e:
        print(f"Error updating recipe for menu item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating recipe"
        )