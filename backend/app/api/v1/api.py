from fastapi import APIRouter

from app.api.v1.endpoints import auth, users
from app.api.v1.endpoints import menu
from app.api.v1.endpoints import inventory
from app.api.v1.endpoints import pos
from app.api.v1.endpoints import reports

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(menu.router, prefix="/menu", tags=["Menu"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(pos.router, prefix="/pos", tags=["POS"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
