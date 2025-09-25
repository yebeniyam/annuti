from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timedelta
from dateutil import parser

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.reports import (
    SalesSummary, MenuItemSalesReport, DailySalesReport, 
    WeeklySalesReport, MonthlySalesReport, EmployeePerformanceReport,
    InventoryVarianceReport, WasteReport, DashboardSummary
)

router = APIRouter()

@router.get("/dashboard/summary", response_model=DashboardSummary, summary="Get dashboard summary")
async def get_dashboard_summary(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: object = Depends(get_current_active_user)
):
    """
    Get dashboard summary data for a given period.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - DashboardSummary: Summary of key metrics for the period
    """
    try:
        # Parse dates
        start_dt = parser.parse(start_date).date()
        end_dt = parser.parse(end_date).date()
        
        # Fetch total sales and orders
        sales_result = supabase.client.table('orders').select('*').gte('created_at', start_date).lte('created_at', end_date).execute()
        
        total_sales = 0
        total_orders = 0
        avg_order_value = 0
        
        if sales_result.data:
            total_orders = len(sales_result.data)
            total_sales = sum(order.get('total', 0) for order in sales_result.data)
            if total_orders > 0:
                avg_order_value = total_sales / total_orders
        
        # Calculate profit margin (simplified - would need more complex logic for actual COGS)
        profit_margin = 62.0  # Placeholder - should be calculated based on actual data
        
        # Get top selling items (simplified query)
        top_items_result = supabase.client.table('order_items').select(
            'menu_item_id, menu_item_name, SUM(quantity) as total_quantity, SUM(unit_price * quantity) as total_revenue'
        ).gte('created_at', start_date).lte('created_at', end_date).group('menu_item_id, menu_item_name').order('total_quantity', desc=True).limit(5).execute()
        
        top_selling_items = []
        if top_items_result.data:
            for item in top_items_result.data:
                top_selling_items.append(MenuItemSalesReport(
                    menu_item_id=item['menu_item_id'],
                    menu_item_name=item['menu_item_name'],
                    quantity_sold=item['total_quantity'],
                    revenue=item['total_revenue'],
                    cost=item['total_revenue'] * 0.38,  # Placeholder cost calculation
                    profit=item['total_revenue'] * 0.62,  # Placeholder profit calculation
                    profit_margin=62.0  # Placeholder margin
                ))
        
        # Get low stock items
        low_stock_result = supabase.client.table('ingredients').select('*').lte('current_stock', 'min_stock').execute()
        low_stock_items = [item for item in (low_stock_result.data if low_stock_result.data else [])]
        
        # Return dashboard summary
        return DashboardSummary(
            total_sales=total_sales,
            total_orders=total_orders,
            avg_order_value=avg_order_value,
            profit_margin=profit_margin,
            total_expenses=total_sales * 0.38,  # Placeholder
            net_profit=total_sales * 0.62,  # Placeholder
            top_selling_items=top_selling_items,
            low_stock_items=low_stock_items,
            date_range=f"{start_date} to {end_date}"
        )
    except Exception as e:
        print(f"Error getting dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting dashboard summary"
        )


@router.get("/sales", response_model=List[DailySalesReport], summary="Get sales reports")
async def get_sales_reports(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: object = Depends(get_current_active_user)
):
    """
    Get sales reports for a given period.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - List of DailySalesReport objects
    """
    try:
        # Parse dates
        start_dt = parser.parse(start_date).date()
        end_dt = parser.parse(end_date).date()
        
        # For each date in the range, calculate sales metrics
        reports = []
        current_date = start_dt
        
        while current_date <= end_dt:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Fetch orders for the specific date
            orders_result = supabase.client.table('orders').select('*').eq('created_at', date_str).execute()
            
            total_sales = 0
            total_orders = 0
            avg_order_value = 0
            daily_items = []
            
            if orders_result.data:
                total_orders = len(orders_result.data)
                total_sales = sum(order.get('total', 0) for order in orders_result.data)
                if total_orders > 0:
                    avg_order_value = total_sales / total_orders
                
                # Get items for top selling items on this day
                day_items_result = supabase.client.table('order_items').select(
                    'menu_item_id, menu_item_name, SUM(quantity) as total_quantity, SUM(unit_price * quantity) as total_revenue'
                ).eq('created_at', date_str).group('menu_item_id, menu_item_name').order('total_quantity', desc=True).execute()
                
                if day_items_result.data:
                    for item in day_items_result.data:
                        daily_items.append(MenuItemSalesReport(
                            menu_item_id=item['menu_item_id'],
                            menu_item_name=item['menu_item_name'],
                            quantity_sold=item['total_quantity'],
                            revenue=item['total_revenue'],
                            cost=item['total_revenue'] * 0.38,  # Placeholder
                            profit=item['total_revenue'] * 0.62,  # Placeholder
                            profit_margin=62.0
                        ))
            
            reports.append(DailySalesReport(
                date=date_str,
                total_sales=total_sales,
                total_orders=total_orders,
                avg_order_value=avg_order_value,
                top_selling_items=daily_items
            ))
            
            current_date += timedelta(days=1)
        
        return reports
    except Exception as e:
        print(f"Error getting sales reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting sales reports"
        )


@router.get("/employee-performance", response_model=List[EmployeePerformanceReport], summary="Get employee performance reports")
async def get_employee_performance_reports(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: object = Depends(get_current_active_user)
):
    """
    Get employee performance reports for a given period.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - List of EmployeePerformanceReport objects
    """
    try:
        # Fetch orders by user in the specified date range
        orders_result = supabase.client.table('orders').select(
            'user_id, users!inner(full_name), COUNT(*) as total_orders, SUM(total) as total_sales'
        ).gte('created_at', start_date).lte('created_at', end_date).group('user_id, users.full_name').execute()
        
        performance_reports = []
        if orders_result.data:
            for order_data in orders_result.data:
                user_id = order_data['user_id']
                user_name = order_data['users']['full_name']
                total_orders = int(order_data['total_orders'])
                total_sales = float(order_data['total_sales']) if order_data['total_sales'] else 0
                avg_order_value = total_sales / total_orders if total_orders > 0 else 0
                
                performance_reports.append(EmployeePerformanceReport(
                    employee_id=user_id,
                    employee_name=user_name,
                    total_orders_handled=total_orders,
                    total_sales=total_sales,
                    avg_order_value=avg_order_value,
                    date_range=f"{start_date} to {end_date}"
                ))
        
        return performance_reports
    except Exception as e:
        print(f"Error getting employee performance reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting employee performance reports"
        )


@router.get("/menu-item-performance", response_model=List[MenuItemSalesReport], summary="Get menu item performance reports")
async def get_menu_item_performance_reports(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: object = Depends(get_current_active_user)
):
    """
    Get menu item performance reports for a given period.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - List of MenuItemSalesReport objects
    """
    try:
        # Fetch order items in the specified date range
        items_result = supabase.client.table('order_items').select(
            'menu_item_id, menu_item_name, SUM(quantity) as total_quantity, SUM(unit_price * quantity) as total_revenue'
        ).gte('created_at', start_date).lte('created_at', end_date).group('menu_item_id, menu_item_name').order('total_quantity', desc=True).execute()
        
        item_reports = []
        if items_result.data:
            for item_data in items_result.data:
                # Get the menu item to calculate cost (COGS)
                menu_item_result = supabase.client.table('menu_items').select('cost').eq('id', item_data['menu_item_id']).single().execute()
                
                cost_per_item = 0
                if menu_item_result.data:
                    cost_per_item = menu_item_result.data.get('cost', 0)
                
                total_cost = cost_per_item * item_data['total_quantity']
                total_revenue = item_data['total_revenue']
                profit = total_revenue - total_cost
                profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
                
                item_reports.append(MenuItemSalesReport(
                    menu_item_id=item_data['menu_item_id'],
                    menu_item_name=item_data['menu_item_name'],
                    quantity_sold=item_data['total_quantity'],
                    revenue=total_revenue,
                    cost=total_cost,
                    profit=profit,
                    profit_margin=profit_margin
                ))
        
        return item_reports
    except Exception as e:
        print(f"Error getting menu item performance reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting menu item performance reports"
        )


@router.get("/inventory-variance", response_model=List[InventoryVarianceReport], summary="Get inventory variance reports")
async def get_inventory_variance_reports(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: object = Depends(get_current_active_user)
):
    """
    Get inventory variance reports for a given period.
    This compares theoretical usage vs actual counts.
    
    Parameters:
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    
    Returns:
        - List of InventoryVarianceReport objects
    """
    try:
        # This is a simplified implementation
        # In a real system, we would need to track theoretical usage based on recipes and sales
        # For now, we'll just return the current inventory state
        
        # Get ingredients that have been used in transactions during this period
        transactions_result = supabase.client.table('inventory_transactions').select(
            'id, type, date, inventory_transaction_items!inner(ingredient_id, quantity)'
        ).gte('date', start_date).lte('date', end_date).execute()
        
        # For this simplified version, return ingredients with low stock
        low_stock_result = supabase.client.table('ingredients').select('*').lte('current_stock', 'min_stock').execute()
        
        variance_reports = []
        if low_stock_result.data:
            for ingredient in low_stock_result.data:
                theoretical_usage = ingredient['min_stock']  # Placeholder
                actual_count = ingredient['current_stock']
                variance = actual_count - theoretical_usage
                variance_percentage = (variance / theoretical_usage) * 100 if theoretical_usage > 0 else 0
                
                variance_reports.append(InventoryVarianceReport(
                    ingredient_id=ingredient['id'],
                    ingredient_name=ingredient['name'],
                    theoretical_usage=theoretical_usage,
                    actual_count=actual_count,
                    variance=variance,
                    variance_percentage=variance_percentage,
                    date_range=f"{start_date} to {end_date}"
                ))
        
        return variance_reports
    except Exception as e:
        print(f"Error getting inventory variance reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting inventory variance reports"
        )