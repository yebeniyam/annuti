from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SalesSummaryBase(BaseModel):
    date: str  # Format: YYYY-MM-DD
    total_sales: float = Field(..., ge=0)
    total_tax: float = Field(..., ge=0)
    total_discount: float = Field(..., ge=0)
    total_net: float = Field(..., ge=0)
    total_orders: int = Field(..., ge=0)
    avg_order_value: float = Field(..., ge=0)

class SalesSummaryCreate(SalesSummaryBase):
    pass

class SalesSummaryUpdate(BaseModel):
    total_sales: Optional[float] = Field(None, ge=0)
    total_tax: Optional[float] = Field(None, ge=0)
    total_discount: Optional[float] = Field(None, ge=0)
    total_net: Optional[float] = Field(None, ge=0)
    total_orders: Optional[int] = Field(None, ge=0)
    avg_order_value: Optional[float] = Field(None, ge=0)

class SalesSummary(SalesSummaryBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MenuItemSalesReport(BaseModel):
    menu_item_id: str
    menu_item_name: str
    quantity_sold: int = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    cost: float = Field(..., ge=0)
    profit: float = Field(..., ge=0)
    profit_margin: float = Field(..., ge=0)  # Percentage

class DailySalesReport(BaseModel):
    date: str
    total_sales: float
    total_orders: int
    avg_order_value: float
    top_selling_items: List[MenuItemSalesReport]

class WeeklySalesReport(BaseModel):
    week_start: str  # Format: YYYY-MM-DD
    week_end: str    # Format: YYYY-MM-DD
    total_sales: float
    total_orders: int
    avg_order_value: float
    daily_breakdown: List[DailySalesReport]

class MonthlySalesReport(BaseModel):
    month: str  # Format: YYYY-MM
    total_sales: float
    total_orders: int
    avg_order_value: float
    weekly_breakdown: List[WeeklySalesReport]

class EmployeePerformanceReport(BaseModel):
    employee_id: str
    employee_name: str
    total_orders_handled: int
    total_sales: float
    avg_order_value: float
    date_range: str  # Format: YYYY-MM-DD to YYYY-MM-DD

class InventoryVarianceReport(BaseModel):
    ingredient_id: str
    ingredient_name: str
    theoretical_usage: float
    actual_count: float
    variance: float
    variance_percentage: float
    date_range: str  # Format: YYYY-MM-DD to YYYY-MM-DD

class WasteReport(BaseModel):
    ingredient_id: str
    ingredient_name: str
    quantity_wasted: float
    cost: float
    reason: str
    date: str  # Format: YYYY-MM-DD

class DashboardSummary(BaseModel):
    total_sales: float
    total_orders: int
    avg_order_value: float
    profit_margin: float
    total_expenses: float
    net_profit: float
    top_selling_items: List[MenuItemSalesReport]
    low_stock_items: List[dict]  # Simplified for now
    date_range: str  # Format: YYYY-MM-DD to YYYY-MM-DD