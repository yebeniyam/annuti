from fastapi import APIRouter
from . import categories, items, recipes

router = APIRouter()

# Include routers
router.include_router(categories.router, prefix="/categories", tags=["Menu Categories"])
router.include_router(items.router, prefix="/items", tags=["Menu Items"])
router.include_router(recipes.router, prefix="/items", tags=["Recipes"])