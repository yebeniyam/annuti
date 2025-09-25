from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.core.security import get_current_active_user, get_admin_user, get_manager_user
from app.core.supabase import supabase
from app.models.inventory import (
    InventoryTransactionCreate, InventoryTransactionUpdate, InventoryTransaction,
    InventoryTransactionItemCreate, InventoryTransactionItemUpdate, InventoryTransactionItem
)

router = APIRouter()

@router.get("/transactions", response_model=List[InventoryTransaction], summary="List inventory transactions")
async def list_transactions(
    current_user: InventoryTransaction = Depends(get_current_active_user)
):
    """
    Retrieve a list of inventory transactions.
    
    Returns:
        - List of inventory transaction objects
    """
    try:
        # Build the query
        query = supabase.client.table('inventory_transactions').select('*').order('date', desc=True)
        
        # Execute the query
        result = query.execute()
        
        # Convert to model objects
        transactions = [InventoryTransaction(**transaction) for transaction in result.data]
        
        return transactions
    except Exception as e:
        print(f"Error retrieving transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving transactions"
        )


@router.post("/transactions", response_model=InventoryTransaction, status_code=status.HTTP_201_CREATED, summary="Create a new inventory transaction")
async def create_transaction(
    transaction: InventoryTransactionCreate,
    current_user: InventoryTransaction = Depends(get_manager_user)
):
    """
    Create a new inventory transaction (receiving, issuing, or adjustment).
    
    Only managers and admins can create inventory transactions.
    
    Parameters:
    - transaction: InventoryTransactionCreate object containing the transaction information
    
    Returns:
        - InventoryTransaction: The created transaction object
    """
    try:
        # Prepare transaction data for database
        transaction_data = transaction.dict(exclude={'items'})
        transaction_data['date'] = datetime.utcnow().isoformat()
        transaction_data['created_at'] = transaction_data['date']
        transaction_data['updated_at'] = transaction_data['date']
        
        # Insert new transaction into database
        result = supabase.client.table('inventory_transactions').insert(transaction_data).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create transaction"
            )
        
        # Get the created transaction ID
        transaction_id = result.data[0]['id']
        
        # Process transaction items
        for item_data in transaction.items:
            item_data['transaction_id'] = transaction_id
            item_data['created_at'] = datetime.utcnow().isoformat()
            item_data['updated_at'] = item_data['created_at']
            
            # Insert transaction item
            supabase.client.table('inventory_transaction_items').insert(item_data).execute()
        
        # Update ingredient stock levels based on transaction type
        for item_data in transaction.items:
            ingredient_id = item_data['ingredient_id']
            quantity = item_data['quantity']
            
            # Get current ingredient
            ingredient_result = supabase.client.table('ingredients').select('current_stock').eq('id', ingredient_id).single().execute()
            if ingredient_result.data:
                current_stock = ingredient_result.data['current_stock']
                
                # Update stock based on transaction type
                if transaction.type == 'receiving':
                    new_stock = current_stock + quantity
                elif transaction.type == 'issuing':
                    new_stock = current_stock - quantity
                else:  # adjustment
                    # For adjustments, we might need additional logic
                    # For now, let's assume positive quantity means increase, negative means decrease
                    new_stock = current_stock + quantity
                
                # Update the ingredient with new stock level
                supabase.client.table('ingredients').update({
                    'current_stock': new_stock,
                    'updated_at': datetime.utcnow().isoformat()
                }).eq('id', ingredient_id).execute()
        
        # Return the created transaction
        created_transaction = result.data[0]
        return InventoryTransaction(**created_transaction)
    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating transaction"
        )


@router.get("/transactions/{transaction_id}", response_model=InventoryTransaction, summary="Get inventory transaction by ID")
async def get_transaction(
    transaction_id: str,
    current_user: InventoryTransaction = Depends(get_current_active_user)
):
    """
    Get a specific inventory transaction by ID.
    
    Parameters:
    - transaction_id: ID of the transaction to retrieve
    
    Returns:
        - InventoryTransaction: The requested transaction object
    """
    try:
        result = supabase.client.table('inventory_transactions').select('*').eq('id', transaction_id).single().execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return InventoryTransaction(**result.data)
    except Exception as e:
        print(f"Error retrieving transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving transaction"
        )


@router.get("/low-stock", response_model=List[object], summary="Get low stock items")
async def get_low_stock_items(
    current_user: object = Depends(get_current_active_user)
):
    """
    Get items that are below their minimum stock level.
    
    Returns:
        - List of items that are low in stock
    """
    try:
        # Get ingredients where current_stock <= min_stock
        result = supabase.client.table('ingredients').select('*').lte('current_stock', 'min_stock').execute()
        
        low_stock_items = []
        if result.data:
            for item in result.data:
                # Calculate how much below minimum the stock is
                shortage = item['min_stock'] - item['current_stock']
                item['shortage'] = shortage
                low_stock_items.append(item)
        
        return low_stock_items
    except Exception as e:
        print(f"Error retrieving low stock items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving low stock items"
        )