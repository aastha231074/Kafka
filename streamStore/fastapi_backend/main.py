from typing import Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from db_config import query_table, add_sale, query_individual_item_price, update_inventory_quantity
import uuid
from fastapi import FastAPI, HTTPException
from typing import List
import sqlite3
from confluent_kafka import Producer
import json

producer_config = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    if err:
        print(f"❌ Order Failed: {err}")
    else:
        print(f"✅ Order Delivered to topic: {msg.topic()} partition: {msg.partition()} offset: {msg.offset()} message value: {msg.value()}")

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
            
            unit_price = query_individual_item_price('ecommerce.db', product_id)
            if unit_price is None:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
            
            # dict for kafka
            order = {
                "order_id": order_id,
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price
            }
            
            value = json.dumps(order).encode('utf-8')
            producer.produce(
                topic='orders', 
                value=value,
                callback=delivery_report 
            )
            
            producer.flush()
        
        return {"order_id": order_id, "status": "success", "message": "Checkout completed successfully"}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

