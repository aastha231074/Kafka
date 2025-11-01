from fastapi import FastAPI, Body
from db_config import query_table

app = FastAPI()

@app.get("/products")
async def read_all_products():
    results = query_table('ecommerce.db', 'inventory')
    return results


