from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    RECEIVING = "receiving"
    ISSUING = "issuing"
    ADJUSTMENT = "adjustment"

class UnitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    abbreviation: str = Field(..., min_length=1, max_length=10)
    base_unit_id: Optional[str] = None
    conversion_factor: Optional[float] = 1.0

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    abbreviation: Optional[str] = Field(None, min_length=1, max_length=10)
    base_unit_id: Optional[str] = None
    conversion_factor: Optional[float] = None

class Unit(UnitBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    unit: str = Field(..., min_length=1, max_length=20)
    current_stock: float = Field(..., ge=0)
    min_stock: float = Field(..., ge=0)  # Minimum stock level
    unit_cost: float = Field(..., ge=0)  # Current unit cost
    supplier_id: Optional[str] = None
    category: Optional[str] = None

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    unit: Optional[str] = Field(None, min_length=1, max_length=20)
    current_stock: Optional[float] = Field(None, ge=0)
    min_stock: Optional[float] = Field(None, ge=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    supplier_id: Optional[str] = None
    category: Optional[str] = None

class Ingredient(IngredientBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryTransactionBase(BaseModel):
    type: TransactionType
    reference_id: Optional[str] = None  # Reference to related entity (PO, order, etc.)
    notes: Optional[str] = None
    user_id: str

class InventoryTransactionCreate(InventoryTransactionBase):
    items: List[dict]  # List of transaction items

class InventoryTransactionUpdate(BaseModel):
    notes: Optional[str] = None

class InventoryTransaction(InventoryTransactionBase):
    id: str
    date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryTransactionItemBase(BaseModel):
    ingredient_id: str
    quantity: float = Field(..., gt=0)
    unit_cost: float = Field(..., ge=0)
    total_cost: float = Field(..., ge=0)
    expiry_date: Optional[str] = None  # Date in ISO format
    batch_number: Optional[str] = None

class InventoryTransactionItemCreate(InventoryTransactionItemBase):
    pass

class InventoryTransactionItemUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    unit_cost: Optional[float] = Field(None, ge=0)
    total_cost: Optional[float] = Field(None, ge=0)
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None

class InventoryTransactionItem(InventoryTransactionItemBase):
    id: str
    transaction_id: str

    class Config:
        from_attributes = True