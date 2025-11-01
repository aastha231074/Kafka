from typing import Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from db_config import query_table, add_sale, query_individual_item_price, update_inventory_quantity
import uuid
from fastapi import FastAPI, HTTPException
from typing import List
import sqlite3

app = FastAPI()

@app.get("/products")
async def read_all_products():
    results = query_table('ecommerce.db', 'inventory')
    return results 

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]

@app.post("/checkout")
async def checkout(order_data: CheckoutRequest):
    order_id = str(uuid.uuid4())  # Generate order ID 
    
    try:
        for item in order_data.items:
            product_id = item.product_id
            quantity = item.quantity
            
            # Validate quantity
            if quantity <= 0:
                raise HTTPException(status_code=400, detail=f"Invalid quantity for product {product_id}")
            
            # Get current price before updating inventory
            unit_price = query_individual_item_price('ecommerce.db', product_id)
            if unit_price is None:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
            # Update inventory
            success = update_inventory_quantity('ecommerce.db', product_id, quantity)
            if not success:
                raise HTTPException(status_code=400, detail=f"Insufficient inventory for product {product_id}")
            
            # Add sale record
            add_sale('ecommerce.db', order_id, product_id, quantity, unit_price)
        
        return {"order_id": order_id, "status": "success", "message": "Checkout completed successfully"}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

