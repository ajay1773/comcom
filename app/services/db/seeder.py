from faker import Faker
from typing import Tuple, List
from app.services.db.db import db_service
import json
import aiohttp

fake = Faker()
Faker.seed(12345)

async def fetch_dummyjson_products() -> List[dict]:
    """Fetch products from DummyJSON API"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://dummyjson.com/products?limit=193') as response:
            data = await response.json()
            return data['products']

def convert_dummyjson_to_tuple(product: dict) -> Tuple:
    """Convert DummyJSON product to database tuple"""
    
    # Use original category from DummyJSON
    category = product['category']
    
    # Sizes logic based on category
    category_lower = category.lower() if category else ''
    if any(term in category_lower for term in ['clothing', 'tops', 'dresses', 'shirts']):
        available_sizes = json.dumps(['XS', 'S', 'M', 'L', 'XL'])
        unit = 'piece'
    elif 'shoes' in category_lower:
        available_sizes = json.dumps(['6', '7', '8', '9', '10', '11'])
        unit = 'pair'
    elif 'bags' in category_lower:
        available_sizes = json.dumps(['Small', 'Medium', 'Large'])
        unit = 'piece'
    elif 'jewellery' in category_lower or 'jewelry' in category_lower:
        available_sizes = json.dumps(['One Size'])
        unit = 'piece'
    else:
        available_sizes = json.dumps(['One Size'])
        unit = 'piece'
    
    # Gender detection from category
    gender = 'U'  # Unisex by default
    if 'women' in category_lower:
        gender = 'F'
    elif 'men' in category_lower:
        gender = 'M'
    
    return (
        product['title'],  # title
        product['description'],  # description
        category,  # category
        product['price'],  # price
        product.get('discountPercentage', 0.0),  # discount_percentage
        product.get('rating', 0.0),  # rating
        product.get('stock', 0),  # stock
        json.dumps(product.get('tags', [])),  # tags
        product.get('brand', fake.company()),  # brand
        product.get('sku', f"SKU-{fake.random_int(100000, 999999)}"),  # sku
        product.get('weight', 0.0),  # weight
        json.dumps(product.get('dimensions', {})),  # dimensions
        product.get('warrantyInformation', ''),  # warranty_information
        product.get('shippingInformation', ''),  # shipping_information
        product.get('availabilityStatus', 'In Stock'),  # availability_status
        product.get('returnPolicy', ''),  # return_policy
        product.get('minimumOrderQuantity', 1),  # minimum_order_quantity
        product.get('thumbnail', ''),  # thumbnail
        json.dumps(product.get('images', [])),  # images
        product.get('meta', {}).get('barcode', ''),  # barcode
        product.get('meta', {}).get('qrCode', ''),  # qr_code
        available_sizes,  # available_sizes
        unit,  # unit
        gender  # gender
    )


async def seed_database(num_products: int = 100) -> None:
    """
    Seed database with products from DummyJSON API only
    """
    # Check if already seeded
    existing_products = await db_service.execute_query("SELECT COUNT(*) FROM products")
    if existing_products and existing_products[0][0] > 0:
        print("Database already seeded, skipping...")
        return

    # Create table with updated schema (with gender field)
    await db_service.execute_query("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            discount_percentage REAL DEFAULT 0.0,
            rating REAL DEFAULT 0.0,
            stock INTEGER DEFAULT 0,
            tags TEXT NOT NULL DEFAULT '[]',
            brand TEXT NOT NULL,
            sku TEXT NOT NULL,
            weight REAL DEFAULT 0.0,
            dimensions TEXT NOT NULL DEFAULT '{}',
            warranty_information TEXT DEFAULT '',
            shipping_information TEXT DEFAULT '',
            availability_status TEXT DEFAULT 'In Stock',
            return_policy TEXT DEFAULT '',
            minimum_order_quantity INTEGER DEFAULT 1,
            thumbnail TEXT NOT NULL,
            images TEXT NOT NULL DEFAULT '[]',
            barcode TEXT DEFAULT '',
            qr_code TEXT DEFAULT '',
            available_sizes TEXT NOT NULL DEFAULT '[]',
            unit TEXT NOT NULL DEFAULT 'piece',
            gender TEXT
        )
    """)

    products = []
    
    try:
        # Get all products from DummyJSON API
        api_products = await fetch_dummyjson_products()
        products.extend([
            convert_dummyjson_to_tuple(p) 
            for p in api_products
        ])
        print(f"Fetched {len(products)} products from DummyJSON")
    except Exception as e:
        print(f"Failed to fetch from API: {e}")
        return
    
    # Insert products
    await db_service.execute_query(
        """
        INSERT INTO products (title, description, category, price, discount_percentage, rating, stock, tags, brand, sku, weight, dimensions, warranty_information, shipping_information, availability_status, return_policy, minimum_order_quantity, thumbnail, images, barcode, qr_code, available_sizes, unit, gender)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products
    )

    print(f"Seeded database with {len(products)} products from DummyJSON")