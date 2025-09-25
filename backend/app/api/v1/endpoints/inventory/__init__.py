from fastapi import APIRouter
from . import items, transactions

router = APIRouter()

# Include routers
router.include_router(items.router, prefix="", tags=["Inventory Items & Units"])
router.include_router(transactions.router, prefix="", tags=["Inventory Transactions"])