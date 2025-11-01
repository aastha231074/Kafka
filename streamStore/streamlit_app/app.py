import streamlit as st 
import os
import requests 

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="streamStore 🛒", layout="wide")
st.title("🛒 Stream Store")

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state.cart = []


# Sidebar: Shopping Cart Display
with st.sidebar: 
    st.header('🛍️ Shopping Cart')
    if not st.session_state.cart:
        st.write("🛒 Your cart is empty. Keep shopping!")
    else:
        total = 0.0
        for item in st.session_state.cart:
            st.markdown(f"**{item['name']}** — {item['quantity']} x ${item['price']:.2f}")
            total += item['price'] * item['quantity']
        st.markdown(f"### 💰 Total: ${total:.2f}")
        if st.button("Checkout", use_container_width=True):
            st.success("✅ Order placed! (Not implemented yet)")
            st.session_state.cart = []  # Clear cart after checkout
            st.rerun()


# products = [
#     {"product_id": 1, "product_name": "Laptop", "price": 999.99, "quantity_in_stock": 10, "category": "High-performance laptop"},
#     {"product_id": 2, "product_name": "Mouse", "price": 29.99, "quantity_in_stock": 50, "category": "Wireless mouse"},
#     {"product_id": 3, "product_name": "Mechanical Keyboard", "price": 79.99, "quantity_in_stock": 30, "category": "RGB mechanical keyboard"},
#     {"product_id": 4, "product_name": "Monitor", "price": 199.99, "quantity_in_stock": 15, "category": "24-inch Full HD monitor"},
# ]
response = requests.get(f"{BACKEND_URL}/products")
if response.status_code == 200:
    products = response.json()

# Display products in columns
cols = st.columns(3)
for idx, product in enumerate(products):
    with cols[idx % 3]:
        st.markdown(f"""
            <div>
                <h4>{product['product_name']}</h4>
                <p><em>{product['category']}</em></p>
                <p><strong>Price: ${product['price']:.2f}</strong></p>
                <p>📦 In stock: {product['quantity_in_stock']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=product['quantity_in_stock'],
            value=1,
            key=f"qty_{product['product_id']}"
        )                    
        
        if st.button(f"Add to Cart", key=f"add_{product['product_id']}", use_container_width=True):
            # Check if product already in cart
            existing_item = None
            for item in st.session_state.cart:
                if item['product_id'] == product['product_id']:
                    existing_item = item
                    break
            
            if existing_item:
                # Update quantity if not exceeding stock
                new_qty = existing_item['quantity'] + quantity
                if new_qty <= product['quantity_in_stock']:
                    existing_item['quantity'] = new_qty
                    st.success(f"Updated cart: {existing_item['name']} × {new_qty}")
                else:
                    st.warning(f"⚠️ Only {product['quantity_in_stock']} available in stock.")
            else:
                # Add new item
                st.session_state.cart.append({
                    'product_id': product['product_id'],
                    'name': product['product_name'],
                    'price': product['price'],
                    'quantity': quantity
                })
                st.success(f"✅ Added {quantity} × {product['product_name']} to cart!")
            
            st.rerun()  # Refresh UI to show updated cart