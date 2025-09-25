from fastapi import APIRouter
from . import routes

router = APIRouter()

# Include routers
router.include_router(routes.router, prefix="", tags=["POS"])