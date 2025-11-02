import json
import sqlite3
from confluent_kafka import Consumer, KafkaError

consumer_config = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order-tracker",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False  # Manual commit for reliability
}

consumer = Consumer(consumer_config)
consumer.subscribe(["orders"])

print("🟢 Consumer is running and subscribed to orders topic")

def process_order(order):
    """
    Process a single order item with transaction safety.
    Returns True if successful, False otherwise.
    """
    order_id = order['order_id']
    product_id = order['product_id']
    quantity = order['quantity']
    unit_price = order['unit_price']
    
    print(f"📦 Processing order {order_id}: Product {product_id}, Quantity {quantity}")
    
    # Single database connection for transaction
    conn = sqlite3.connect('ecommerce.db')
    
    try:
        conn.execute("BEGIN TRANSACTION")
        cursor = conn.cursor()
        
        # Check if product exists and has sufficient inventory
        cursor.execute(
            "SELECT quantity_in_stock FROM inventory WHERE product_id = ?", 
            (product_id,)
        )
        result = cursor.fetchone()
        
        if result is None:
            print(f"❌ Product {product_id} not found in inventory")
            conn.rollback()
            return False
            
        current_stock = result[0]
        if current_stock < quantity:
            print(f"❌ Insufficient inventory for product {product_id}. Available: {current_stock}, Requested: {quantity}")
            conn.rollback()
            return False
        
        # Update inventory - reduce stock
        new_stock = current_stock - quantity
        cursor.execute(
            "UPDATE inventory SET quantity_in_stock = ? WHERE product_id = ?",
            (new_stock, product_id)
        )
        
        # Add sale record
        subtotal = quantity * unit_price
        cursor.execute(
            """INSERT INTO sales (order_id, product_id, quantity, unit_price, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (order_id, product_id, quantity, unit_price, subtotal)
        )
        
        # Commit both operations together
        conn.commit()
        print(f"✅ Order {order_id} processed successfully - Product {product_id}, New stock: {new_stock}")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error processing order {order_id}: {str(e)}")
        conn.rollback()
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error processing order {order_id}: {str(e)}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None:
            continue
            
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition, not an error
                continue
            else:
                print(f"❌ Kafka Error: {msg.error()}")
                continue
        
        try:
            # Parse message
            value = msg.value().decode("utf-8")
            order = json.loads(value)
            
            # Validate required fields
            required_fields = ['order_id', 'product_id', 'quantity', 'unit_price']
            if not all(field in order for field in required_fields):
                print(f"❌ Invalid message format, missing fields: {value}")
                consumer.commit(msg)  # Skip invalid messages
                continue
            
            # Validate data types and values
            if order['quantity'] <= 0:
                print(f"❌ Invalid quantity: {order['quantity']}")
                consumer.commit(msg)  # Skip invalid data
                continue
            
            # Process the order
            success = process_order(order)
            
            if success:
                # Commit offset only after successful processing
                consumer.commit(msg)
            else:
                # Failed to process - commit anyway to avoid infinite retries
                # In production, send to dead letter queue for manual review
                print(f"⚠️ Committing failed message to prevent reprocessing loop")
                consumer.commit(msg)
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON message: {e}")
            consumer.commit(msg)  # Skip malformed messages
            
        except KeyError as e:
            print(f"❌ Missing required field in message: {e}")
            consumer.commit(msg)  # Skip incomplete messages
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            # Don't commit - allow retry on next poll
            import traceback
            traceback.print_exc()

except KeyboardInterrupt:
    print("\n🔴 Stopping consumer gracefully...")

finally:
    consumer.close()
    print("🔴 Consumer closed")