from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user, get_staff_user
from app.core.supabase import supabase
from app.models.pos import (
    TableCreate, TableUpdate, Table,
    OrderCreate, OrderUpdate, Order,
    OrderItemCreate, OrderItemUpdate, OrderItem,
    PaymentCreate, PaymentUpdate, Payment
)

router = APIRouter()

# Tables endpoints
@router.get("/tables", response_model=List[Table], summary="List all tables")
async def list_tables(
    current_user: Table = Depends(get_current_active_user)
):
    """
    Retrieve a list of all tables.
    
    Returns:
        - List of table objects
    """
    try:
        # Build the query
        query = supabase.client.table('tables').select('*').order('name')
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        tables = [Table(**table) for table in result.data]
        
        return tables
    except Exception as e:
        print(f"Error retrieving tables: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tables"
        )


@router.post("/tables", response_model=Table, status_code=status.HTTP_201_CREATED, summary="Create a new table")
async def create_table(
    table: TableCreate,
    current_user: Table = Depends(get_manager_user)
):
    """
    Create a new table.
    
    Only managers and admins can create tables.
    
    Parameters:
    - table: TableCreate object containing the table information
    
    Returns:
        - Table: The created table object
    """
    try:
        # Prepare table data for database
        table_data = table.dict()
        table_data['created_at'] = datetime.utcnow().isoformat()
        table_data['updated_at'] = table_data['created_at']
        
        # Insert new table into database
        result = supabase.client.table('tables').insert(table_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create table"
            )
        
        # Return the created table
        created_table = result.data[0]
        return Table(**created_table)
    except Exception as e:
        print(f"Error creating table: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating table"
        )


@router.get("/tables/{table_id}", response_model=Table, summary="Get table by ID")
async def get_table(
    table_id: str,
    current_user: Table = Depends(get_current_active_user)
):
    """
    Get a specific table by ID.
    
    Parameters:
    - table_id: ID of the table to retrieve
    
    Returns:
        - Table: The requested table object
    """
    try:
        result = supabase.client.table('tables').select('*').eq('id', table_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
        
        return Table(**result.data)
    except Exception as e:
        print(f"Error retrieving table {table_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving table"
        )


@router.put("/tables/{table_id}", response_model=Table, summary="Update a table")
async def update_table(
    table_id: str,
    table_update: TableUpdate,
    current_user: Table = Depends(get_manager_user)
):
    """
    Update a table.
    
    Only managers and admins can update tables.
    
    Parameters:
    - table_id: ID of the table to update
    - table_update: TableUpdate object containing the fields to update
    
    Returns:
        - Table: The updated table object
    """
    try:
        # Get current table to check if it exists
        current_table_result = supabase.client.table('tables').select('*').eq('id', table_id).single().execute()
        
        if not current_table_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
        
        # Prepare update data
        update_data = table_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update the table in database
        result = supabase.client.table('tables').update(update_data).eq('id', table_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
        
        # Return the updated table
        updated_table = result.data[0]
        return Table(**updated_table)
    except Exception as e:
        print(f"Error updating table {table_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating table"
        )


@router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a table")
async def delete_table(
    table_id: str,
    current_user: Table = Depends(get_admin_user)
):
    """
    Delete a table.
    
    Only admins can delete tables.
    
    Parameters:
    - table_id: ID of the table to delete
    
    Returns:
        - 204 No Content on success
    """
    try:
        # Check if table exists
        current_table_result = supabase.client.table('tables').select('*').eq('id', table_id).single().execute()
        
        if not current_table_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
        
        # Check if the table has any active orders
        active_orders_result = supabase.client.table('orders').select('id').eq('table_id', table_id).in_('status', ['new', 'preparing', 'ready', 'served']).execute()
        if active_orders_result.data and len(active_orders_result.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete table: it has active orders"
            )
        
        # Delete the table
        result = supabase.client.table('tables').delete().eq('id', table_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found"
            )
            
        return None  # 204 No Content
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting table {table_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting table"
        )


# Orders endpoints
@router.get("/orders", response_model=List[Order], summary="List orders")
async def list_orders(
    current_user: Order = Depends(get_current_active_user)
):
    """
    Retrieve a list of orders.
    
    Returns:
        - List of order objects
    """
    try:
        # Build the query with joins to get table name
        query = supabase.client.table('orders').select(
            'id, table_id, status, customer_name, customer_phone, party_size, order_type, subtotal, tax, discount, total, payment_status, created_at, updated_at, tables!inner(name)'
        ).order('created_at', desc=True)
        
        # Execute the query
        result = query.execute()
        
        # Process the result to include table name
        orders = []
        for order_data in result.data:
            table_name = order_data.pop('tables', {}).get('name', '')
            order_data['table_name'] = table_name
            
            # Get order items
            items_result = supabase.client.table('order_items').select('*').eq('order_id', order_data['id']).execute()
            order_data['items'] = [OrderItem(**item) for item in items_result.data] if items_result.data else []
            
            orders.append(Order(**order_data))
        
        return orders
    except Exception as e:
        print(f"Error retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving orders"
        )


@router.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED, summary="Create a new order")
async def create_order(
    order: OrderCreate,
    current_user: Order = Depends(get_staff_user)
):
    """
    Create a new order.
    
    Staff members, managers, and admins can create orders.
    
    Parameters:
    - order: OrderCreate object containing the order information
    
    Returns:
        - Order: The created order object
    """
    try:
        # Prepare order data for database
        order_data = order.dict(exclude={'items'})
        order_data['user_id'] = current_user.id
        order_data['created_at'] = datetime.utcnow().isoformat()
        order_data['updated_at'] = order_data['created_at']
        
        # Insert new order into database
        result = supabase.client.table('orders').insert(order_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order"
            )
        
        # Get the created order ID
        order_id = result.data[0]['id']
        
        # Process order items
        total_cost = 0
        for item_data in order.items:
            item_data['order_id'] = order_id
            item_data['created_at'] = datetime.utcnow().isoformat()
            item_data['updated_at'] = item_data['created_at']
            
            # Insert order item
            item_result = supabase.client.table('order_items').insert(item_data).execute()
            
            # Add to total cost
            if item_result.data and len(item_result.data) > 0:
                item = item_result.data[0]
                total_cost += item['unit_price'] * item['quantity']
        
        # Update order with calculated total (this would typically happen elsewhere)
        # For now, just return the created order
        
        # Get the created order with items
        order_result = supabase.client.table('orders').select('*').eq('id', order_id).single().execute()
        if not order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found after creation"
            )
        
        order_data = order_result.data
        # Get order items
        items_result = supabase.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_data['items'] = [OrderItem(**item) for item in items_result.data] if items_result.data else []
        
        # Update table status to occupied if needed
        supabase.client.table('tables').update({
            'status': 'occupied',
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', order.table_id).execute()
        
        return Order(**order_data)
    except Exception as e:
        print(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating order"
        )


@router.get("/orders/{order_id}", response_model=Order, summary="Get order by ID")
async def get_order(
    order_id: str,
    current_user: Order = Depends(get_current_active_user)
):
    """
    Get a specific order by ID.
    
    Parameters:
    - order_id: ID of the order to retrieve
    
    Returns:
        - Order: The requested order object
    """
    try:
        # Get the order with table join
        result = supabase.client.table('orders').select(
            'id, table_id, status, customer_name, customer_phone, party_size, order_type, subtotal, tax, discount, total, payment_status, created_at, updated_at, tables!inner(name)'
        ).eq('id', order_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_data = result.data
        table_name = order_data.pop('tables', {}).get('name', '')
        order_data['table_name'] = table_name
        
        # Get order items
        items_result = supabase.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_data['items'] = [OrderItem(**item) for item in items_result.data] if items_result.data else []
        
        return Order(**order_data)
    except Exception as e:
        print(f"Error retrieving order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving order"
        )


@router.put("/orders/{order_id}", response_model=Order, summary="Update an order")
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: Order = Depends(get_staff_user)
):
    """
    Update an order.
    
    Staff members, managers, and admins can update orders.
    
    Parameters:
    - order_id: ID of the order to update
    - order_update: OrderUpdate object containing the fields to update
    
    Returns:
        - Order: The updated order object
    """
    try:
        # Get current order to check if it exists
        current_order_result = supabase.client.table('orders').select('*').eq('id', order_id).single().execute()
        
        if not current_order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Prepare update data
        update_data = order_update.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update the order in database
        result = supabase.client.table('orders').update(update_data).eq('id', order_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Get the updated order
        updated_order_result = supabase.client.table('orders').select('*').eq('id', order_id).single().execute()
        if not updated_order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found after update"
            )
        
        order_data = updated_order_result.data
        # Get order items
        items_result = supabase.client.table('order_items').select('*').eq('order_id', order_id).execute()
        order_data['items'] = [OrderItem(**item) for item in items_result.data] if items_result.data else []
        
        # If order status is updated to 'paid', update table status to 'dirty'
        if 'status' in update_data and update_data['status'] == 'paid':
            supabase.client.table('tables').update({
                'status': 'dirty',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', order_data['table_id']).execute()
        
        return Order(**order_data)
    except Exception as e:
        print(f"Error updating order {order_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating order"
        )


# Payments endpoints
@router.get("/payments", response_model=List[Payment], summary="List payments")
async def list_payments(
    current_user: Payment = Depends(get_current_active_user)
):
    """
    Retrieve a list of payments.
    
    Returns:
        - List of payment objects
    """
    try:
        # Build the query
        query = supabase.client.table('payments').select('*').order('created_at', desc=True)
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        payments = [Payment(**payment) for payment in result.data]
        
        return payments
    except Exception as e:
        print(f"Error retrieving payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving payments"
        )


@router.post("/payments", response_model=Payment, status_code=status.HTTP_201_CREATED, summary="Process a payment")
async def process_payment(
    payment: PaymentCreate,
    current_user: Payment = Depends(get_staff_user)
):
    """
    Process a payment for an order.
    
    Staff members, managers, and admins can process payments.
    
    Parameters:
    - payment: PaymentCreate object containing the payment information
    
    Returns:
        - Payment: The created payment object
    """
    try:
        # Verify order exists and get current status
        order_result = supabase.client.table('orders').select('total, payment_status').eq('id', payment.order_id).single().execute()
        if not order_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order_data = order_result.data
        order_total = order_data['total']
        
        # Check if payment amount matches order total (for full payment)
        if payment.amount == order_total:
            # Update order payment status to paid
            supabase.client.table('orders').update({
                'payment_status': 'paid',
                'status': 'paid',  # Also update order status to paid
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', payment.order_id).execute()
        else:
            # Partial payment
            supabase.client.table('orders').update({
                'payment_status': 'partial',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', payment.order_id).execute()
        
        # Prepare payment data for database
        payment_data = payment.dict()
        payment_data['user_id'] = current_user.id
        payment_data['created_at'] = datetime.utcnow().isoformat()
        payment_data['updated_at'] = payment_data['created_at']
        
        # Insert new payment into database
        result = supabase.client.table('payments').insert(payment_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment"
            )
        
        # Return the created payment
        created_payment = result.data[0]
        return Payment(**created_payment)
    except Exception as e:
        print(f"Error processing payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing payment"
        )