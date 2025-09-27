from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    NEW = "new"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"

class OrderType(str, Enum):
    DINE_IN = "dine-in"
    TAKEOUT = "takeout"
    DELIVERY = "delivery"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    TELEBIRR = "telebirr"
    CHAPA = "chapa"

class TableBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0)
    status: str = Field(default="available", pattern=r"^(available|occupied|reserved|dirty)$")
    section_id: Optional[str] = None

    pass

class TableUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern=r"^(available|occupied|reserved|dirty)$")
    section_id: Optional[str] = None

class Table(TableBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
class OrderItemBase(BaseModel):
    menu_item_id: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    notes: Optional[str] = None
    status: str = Field(default="new", pattern=r"^(new|preparing|ready|served)$")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(new|preparing|ready|served)$")

class OrderItem(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    status: str = Field(default="pending", pattern=r"^(pending|completed|failed)$")
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(pending|completed|failed)$")
    notes: Optional[str] = None

class Payment(PaymentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True