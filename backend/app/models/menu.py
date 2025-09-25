from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class MenuCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = 0
    is_active: bool = True

class MenuCategoryCreate(MenuCategoryBase):
    pass

class MenuCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class MenuCategory(MenuCategoryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    cost: float = Field(..., ge=0)  # COGS
    category_id: str
    is_available: bool = True
    image_url: Optional[str] = None
    prep_time: Optional[int] = None  # in minutes
    is_featured: bool = False

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    cost: Optional[float] = Field(None, ge=0)
    category_id: Optional[str] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    prep_time: Optional[int] = None
    is_featured: Optional[bool] = None

class MenuItem(MenuItemBase):
    id: str
    category_name: str  # Added for display purposes
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RecipeIngredientBase(BaseModel):
    ingredient_id: str
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=20)
    notes: Optional[str] = None

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredientUpdate(BaseModel):
    ingredient_id: Optional[str] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    notes: Optional[str] = None

class RecipeIngredient(RecipeIngredientBase):
    id: str
    recipe_id: str

    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    instructions: Optional[str] = None
    yield_count: Optional[int] = 1  # How many servings this recipe yields
    yield_unit: Optional[str] = "servings"

class RecipeCreate(RecipeBase):
    ingredients: Optional[List[RecipeIngredientCreate]] = []

class RecipeUpdate(BaseModel):
    instructions: Optional[str] = None
    yield_count: Optional[int] = None
    yield_unit: Optional[str] = None
    ingredients: Optional[List[RecipeIngredientCreate]] = None

class Recipe(RecipeBase):
    id: str
    menu_item_id: str
    ingredients: List[RecipeIngredient] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True