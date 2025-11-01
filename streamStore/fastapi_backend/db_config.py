import sqlite3
from datetime import datetime
import random
import json

def create_database(db_name='ecommerce.db'):
    """Create the database and tables"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create Inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            quantity_in_stock INTEGER NOT NULL,
            supplier TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_email TEXT,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            shipping_address TEXT
        )
    ''')
    
    # Create Sales table (junction table linking orders and products)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES inventory(product_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully!")

def add_sample_data(db_name='ecommerce.db'):
    """Add sample test data to all tables"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Sample inventory data
    inventory_data = [
        ('Laptop Pro 15"', 'Electronics', 1299.99, 45, 'TechSupply Co'),
        ('Wireless Mouse', 'Electronics', 29.99, 150, 'TechSupply Co'),
        ('USB-C Cable', 'Accessories', 12.99, 200, 'Cable World'),
        ('Desk Chair Ergonomic', 'Furniture', 249.99, 30, 'Office Depot'),
        ('Standing Desk', 'Furniture', 399.99, 20, 'Office Depot'),
        ('Mechanical Keyboard', 'Electronics', 89.99, 75, 'TechSupply Co'),
        ('Monitor 27"', 'Electronics', 349.99, 40, 'Display Masters'),
        ('Webcam HD', 'Electronics', 79.99, 60, 'TechSupply Co'),
        ('Desk Lamp LED', 'Accessories', 34.99, 100, 'LightCo'),
        ('Notebook Set', 'Stationery', 15.99, 300, 'Paper Plus')
    ]
    
    cursor.executemany('''
        INSERT INTO inventory (product_name, category, price, quantity_in_stock, supplier)
        VALUES (?, ?, ?, ?, ?)
    ''', inventory_data)
    
    # Sample orders data
    orders_data = [
        ('John Doe', 'john.doe@email.com', 1729.97, 'completed', '123 Main St, New York, NY 10001'),
        ('Jane Smith', 'jane.smith@email.com', 449.98, 'shipped', '456 Oak Ave, Los Angeles, CA 90001'),
        ('Bob Johnson', 'bob.j@email.com', 89.99, 'pending', '789 Pine Rd, Chicago, IL 60601'),
        ('Alice Brown', 'alice.b@email.com', 1684.96, 'completed', '321 Elm St, Houston, TX 77001'),
        ('Charlie Wilson', 'charlie.w@email.com', 364.98, 'shipped', '654 Maple Dr, Phoenix, AZ 85001')
    ]
    
    cursor.executemany('''
        INSERT INTO orders (customer_name, customer_email, total_amount, status, shipping_address)
        VALUES (?, ?, ?, ?, ?)
    ''', orders_data)
    
    # Sample sales data (linking orders to products)
    sales_data = [
        (1, 1, 1, 1299.99, 1299.99),  # Order 1: Laptop
        (1, 2, 1, 29.99, 29.99),       # Order 1: Mouse
        (1, 6, 1, 89.99, 89.99),       # Order 1: Keyboard
        (1, 9, 1, 34.99, 34.99),       # Order 1: Lamp
        (2, 5, 1, 399.99, 399.99),     # Order 2: Standing Desk
        (2, 9, 1, 34.99, 34.99),       # Order 2: Lamp
        (3, 6, 1, 89.99, 89.99),       # Order 3: Keyboard
        (4, 1, 1, 1299.99, 1299.99),   # Order 4: Laptop
        (4, 7, 1, 349.99, 349.99),     # Order 4: Monitor
        (4, 9, 1, 34.99, 34.99),       # Order 4: Lamp
        (5, 4, 1, 249.99, 249.99),     # Order 5: Chair
        (5, 8, 1, 79.99, 79.99),       # Order 5: Webcam
        (5, 9, 1, 34.99, 34.99)        # Order 5: Lamp
    ]
    
    cursor.executemany('''
        INSERT INTO sales (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (?, ?, ?, ?, ?)
    ''', sales_data)
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

def add_inventory_item(db_name, product_name, category, price, quantity, supplier):
    """Add a new product to inventory"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO inventory (product_name, category, price, quantity_in_stock, supplier)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_name, category, price, quantity, supplier))
    
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    print(f"Added product with ID: {product_id}")
    return product_id

def add_order(db_name, customer_name, customer_email, total_amount, status, shipping_address):
    """Add a new order"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO orders (customer_name, customer_email, total_amount, status, shipping_address)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_name, customer_email, total_amount, status, shipping_address))
    
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    print(f"Added order with ID: {order_id}")
    return order_id

def add_sale(db_name, order_id, product_id, quantity, unit_price):
    """Add a sale record"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    subtotal = quantity * unit_price
    cursor.execute('''
        INSERT INTO sales (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (?, ?, ?, ?, ?)
    ''', (order_id, product_id, quantity, unit_price, subtotal))
    
    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()
    print(f"Added sale with ID: {sale_id}")
    return sale_id

def query_table_internal(db_name, table_name, conditions=None, limit=None):
    """
    Query a table with optional conditions
    
    Args:
        db_name: Database name
        table_name: Name of the table to query
        conditions: Optional WHERE clause (e.g., "price > 100")
        limit: Optional limit on number of results
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    query = f"SELECT * FROM {table_name}"
    if conditions:
        query += f" WHERE {conditions}"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    results = json.dumps(results, indent=2, default=str)
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    conn.close()
    
    print(f"\nQuery Results from '{table_name}':")
    print("-" * 80)
    print(" | ".join(column_names))
    print("-" * 80)
    for row in results:
        print(" | ".join(str(item) for item in row))
    print("-" * 80)
    print(f"Total rows: {len(results)}\n")
    
    return results

def query_table(db_name, table_name):
    """
    Query all rows from a SQLite table and return as JSON string.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # enables dict-like access
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    conn.close()
    
    # Convert rows to list of dicts, then to JSON
    results = [dict(row) for row in rows]
    return json.dumps(results, indent=2)

def query_custom(db_name, sql_query):
    """Execute a custom SQL query"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute(sql_query)
    results = cursor.fetchall()
    
    # Get column names
    column_names = [description[0] for description in cursor.description]
    
    conn.close()
    
    print("\nCustom Query Results:")
    print("-" * 80)
    print(" | ".join(column_names))
    print("-" * 80)
    for row in results:
        print(" | ".join(str(item) for item in row))
    print("-" * 80)
    print(f"Total rows: {len(results)}\n")
    
    return results

# Example usage
if __name__ == "__main__":
    DB_NAME = 'ecommerce.db'
    
    # Create database and tables
    # create_database(DB_NAME)
    
    # Add sample data
    # add_sample_data(DB_NAME)
    
    # Query examples
    print("\n=== ALL INVENTORY ===")
    query_table_internal(DB_NAME, 'inventory')
    
    # print("\n=== PRODUCTS UNDER $50 ===")
    # query_table(DB_NAME, 'inventory', conditions="price < 50")
    
    print("\n=== ALL ORDERS ===")
    query_table_internal(DB_NAME, 'orders')
    
    # print("\n=== COMPLETED ORDERS ===")
    # query_table(DB_NAME, 'orders', conditions="status = 'completed'")
    
    # print("\n=== ALL SALES ===")
    # query_table(DB_NAME, 'sales')
    
    # Custom query example - Join tables
    # print("\n=== SALES WITH PRODUCT DETAILS ===")
    # query_custom(DB_NAME, '''
    #     SELECT s.sale_id, o.customer_name, i.product_name, 
    #            s.quantity, s.unit_price, s.subtotal, s.sale_date
    #     FROM sales s
    #     JOIN orders o ON s.order_id = o.order_id
    #     JOIN inventory i ON s.product_id = i.product_id
    #     ORDER BY s.sale_date DESC
    # ''')
    
    # Add new items examples
    # print("\n=== ADDING NEW DATA ===")
    # add_inventory_item(DB_NAME, 'Wireless Headphones', 'Electronics', 129.99, 80, 'Audio Pro')
    # add_order(DB_NAME, 'Sarah Davis', 'sarah.d@email.com', 129.99, 'pending', '999 Broadway, Seattle, WA 98101')