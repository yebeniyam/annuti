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
    status: str = Field(default="available", regex=r"^(available|occupied|reserved|dirty)$")
    section_id: Optional[str] = None

class TableCreate(TableBase):
    pass

class TableUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, regex=r"^(available|occupied|reserved|dirty)$")
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
    status: str = Field(default="new", regex=r"^(new|preparing|ready|served)$")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, regex=r"^(new|preparing|ready|served)$")

class OrderItem(OrderItemBase):
    id: str
    order_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    table_id: str
    order_type: OrderType = OrderType.DINE_IN
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    party_size: Optional[int] = None
    status: OrderStatus = OrderStatus.NEW
    subtotal: float = Field(default=0, ge=0)
    tax: float = Field(default=0, ge=0)
    discount: float = Field(default=0, ge=0)
    total: float = Field(default=0, ge=0)
    payment_status: PaymentStatus = PaymentStatus.PENDING

class OrderCreate(OrderBase):
    items: List[dict]  # List of order items

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    party_size: Optional[int] = None
    payment_status: Optional[PaymentStatus] = None

class Order(OrderBase):
    id: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True

class PaymentBase(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_id: Optional[str] = None
    status: str = Field(default="pending", regex=r"^(pending|completed|failed)$")
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[str] = Field(None, regex=r"^(pending|completed|failed)$")
    notes: Optional[str] = None

class Payment(PaymentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True