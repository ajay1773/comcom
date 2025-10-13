import asyncio
from faker import Faker
from typing import Tuple, List, Dict, Any, cast

from langchain_core.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel
from app.services.db.db import db_service
import json
import aiohttp
import logging

from app.services.llm import llm_service

logger = logging.getLogger(__name__)

fake = Faker()
Faker.seed(12345)

class ProductData(BaseModel):
    material: str
    style: str
    pattern: str
    color: str

# Search keyword extraction constants
SEARCH_KEYWORDS = {
    'colors': [
        'red', 'blue', 'navy', 'black', 'white', 'green', 'yellow', 
        'pink', 'purple', 'brown', 'gray', 'grey', 'orange', 'silver', 
        'gold', 'beige', 'tan', 'ivory', 'cream', 'maroon', 'burgundy'
    ],
    'materials': [
        'leather', 'cotton', 'polyester', 'wool', 'silk', 'denim',
        'metal', 'plastic', 'wood', 'glass', 'synthetic', 'mesh',
        'suede', 'velvet', 'canvas', 'nylon', 'rubber', 'aluminum'
    ],
    'styles': [
        'casual', 'formal', 'athletic', 'sports', 'running', 'walking',
        'vintage', 'modern', 'classic', 'slim', 'regular', 'loose',
        'oversized', 'fitted', 'minimalist', 'elegant'
    ]
}

async def fetch_dummyjson_products() -> List[dict]:
    """Fetch products from DummyJSON API"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://dummyjson.com/products?limit=193') as response:
            data = await response.json()
            return data['products']

async def convert_dummyjson_to_tuple(product: dict, ollama_available: bool = True) -> Tuple:
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

    missing_values = await fill_missing_data_for_product(product, ollama_available)
    
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
        gender,  # gender
        missing_values['material'],  # material
        missing_values['style'],  # style
        missing_values['pattern'],  # pattern
        missing_values['color']  # color
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
            gender TEXT,
            material TEXT,
            style TEXT,
            pattern TEXT,
            color TEXT
        )
    """)


    # Create FTS5 table as standalone (not external content)
    try:
        existing_fts = await db_service.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products_fts'"
        )
        
        if not existing_fts or len(existing_fts) == 0:
            await db_service.execute_query("""
                CREATE VIRTUAL TABLE products_fts USING fts5(
                    product_id UNINDEXED,
                    search_text,
                    tokenize='porter unicode61'
                );
            """)
            print("✅ Created FTS5 table")
        else:
            print("FTS5 table already exists")
            
    except Exception as e:
        logger.error(f"Failed to create FTS table: {e}")
        raise


    products = []
    
    # Check Ollama availability once before processing products
    print("Checking Ollama availability...")
    ollama_available = await check_ollama_availability()
    if ollama_available:
        print("✅ Ollama is available - will use LLM to fill missing product data")
    else:
        print("⚠️  Ollama is not available - will use default values for missing product data")
    
    try:
        # Get all products from DummyJSON API
        api_products = await fetch_dummyjson_products()
        products.extend(
            await asyncio.gather(
                *[
                    convert_dummyjson_to_tuple(p, ollama_available) 
                    for p in api_products
                ]
            )
        )
        print(f"Fetched {len(products)} products from DummyJSON")
    except Exception as e:
        print(f"Failed to fetch from API: {e}")
        return
    
    # Insert products
    await db_service.execute_query(
        """
        INSERT INTO products (title, description, category, price, discount_percentage, rating, stock, tags, brand, sku, weight, dimensions, warranty_information, shipping_information, availability_status, return_policy, minimum_order_quantity, thumbnail, images, barcode, qr_code, available_sizes, unit, gender, material, style, pattern, color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products
    )

    print(f"Seeded database with {len(products)} products from DummyJSON")
    
    # Build the FTS index after seeding
    await build_search_index()

async def check_ollama_availability() -> bool:
    """
    Check if Ollama model is available and responsive.
    """
    try:
        # Try a simple test invocation with timeout
        await asyncio.wait_for(
            llm_service.get_ollama_model().ainvoke("test"),
            timeout=5.0
        )
        return True
    except (asyncio.TimeoutError, Exception) as e:
        logger.warning(f"Ollama model not available: {e}")
        return False


async def fill_missing_data_for_product(product: Dict[str, Any], ollama_available: bool = True) -> Dict[str, Any]:
    """
    Fill missing data for products.
    If Ollama is not available, returns default values.
    """
    
    # Return default values if Ollama is not available
    if not ollama_available:
        return {
            'material': None,
            'style': None,
            'pattern': None,
            'color': None
        }

    try:
        filler_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a data enrichment and inference model for product catalog data.

                You are given a JSON object representing a product. 
                Some fields may be missing (null, empty, or absent). 
                Your task is to analyze the available data — including product name, description, brand, category, price, and any other context — and infer the most reasonable missing values.

                You need to create the following fields:
                - material
                - style
                - pattern
                - color

                If a value truly cannot be inferred, return null for that field (do not hallucinate wildly).

                """),

            ("user", """
                Here is the product data:
                {product}

                Return the enriched product data as a valid JSON object.
            """),
        ])
        parsedProduct = {
                "title": product.get('title', ''),
                "description": product.get('description', ''),
                "brand": product.get('brand', ''),
                "category": product.get('category', ''),
                "price": product.get('price', 0),
                "discount_percentage": product.get('discountPercentage', 0),
                "rating": product.get('rating', 0),
                "stock": product.get('stock', 0),
                "tags": product.get('tags', []),
                "sku": product.get('sku', ''),
                "weight": product.get('weight', 0),
                "dimensions": product.get('dimensions', {}),
                "warranty_information": product.get('warrantyInformation', ''),
                "shipping_information": product.get('shippingInformation', ''),
                "availability_status": product.get('availabilityStatus', ''),
                "return_policy": product.get('returnPolicy', ''),
                "minimum_order_quantity": product.get('minimumOrderQuantity', 1),
                "thumbnail": product.get('thumbnail', ''),
                "images": product.get('images', []),
                "barcode": product.get('meta', {}).get('barcode', ''),
                "qr_code": product.get('meta', {}).get('qrCode', ''),
        }
        response = await llm_service.get_ollama_model().with_structured_output(ProductData).ainvoke(filler_prompt.invoke({"product": parsedProduct}))
        print('Id: ', product.get('id', ''), 'Processed product: ',  product.get('title', ''))
        response = cast(ProductData, response)
        return response.model_dump()
    except Exception as e:
        logger.error(f"Failed to fill missing data for product {product.get('id', 'unknown')}: {e}")
        # Return default values on error
        return {
            'material': None,
            'style': None,
            'pattern': None,
            'color': None
        }


async def build_search_index() -> None:
    """
    Build the search index for all products with error handling and progress.
    Run this once after importing products.
    """
    try:
        # Get all products
        products = await db_service.execute_query("SELECT * FROM products")
        
        if not products:
            logger.warning("No products found to index")
            return
        
        total = len(products)
        print(f"Building search index for {total} products...")
        
        # Clear existing data (idempotent operation)
        await db_service.execute_query("DELETE FROM products_fts")
        
        # Build search text for all products with progress indicator
        fts_data = []
        for i, row in enumerate(products, 1):
            # Convert tuple row to dict for create_search_text function
            product = _row_to_dict(row)
            fts_data.append((product['id'], create_search_text(product)))
            
            # Show progress every 50 products or at the end
            if i % 50 == 0 or i == total:
                print(f"  Processed {i}/{total} products...")
        
        # Batch insert - much faster than individual inserts
        await db_service.execute_query(
            "INSERT INTO products_fts(product_id, search_text) VALUES (?, ?)",
            fts_data
        )
        
        # Verify the index was built correctly
        count = await db_service.execute_query("SELECT COUNT(*) FROM products_fts")
        print(f"✅ Search index built successfully! {count[0][0]} products indexed.")
        
    except Exception as e:
        logger.error(f"Failed to build search index: {e}")
        # Cleanup partial data on failure
        try:
            await db_service.execute_query("DELETE FROM products_fts")
        except:
            pass
        raise


def _row_to_dict(row: tuple) -> Dict[str, Any]:
    """
    Convert a database row tuple to a dictionary.
    Matches the column order from the products table schema.
    """
    return {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'category': row[3],
        'price': row[4],
        'discount_percentage': row[5],
        'rating': row[6],
        'stock': row[7],
        'tags': row[8],
        'brand': row[9],
        'sku': row[10],
        'weight': row[11],
        'dimensions': row[12],
        'warranty_information': row[13],
        'shipping_information': row[14],
        'availability_status': row[15],
        'return_policy': row[16],
        'minimum_order_quantity': row[17],
        'thumbnail': row[18],
        'images': row[19],
        'barcode': row[20],
        'qr_code': row[21],
        'available_sizes': row[22],
        'unit': row[23],
        'gender': row[24],
        'material': row[25],
        'style': row[26],
        'pattern': row[27],
        'color': row[28]
    }


def create_search_text(product: Dict[str, Any]) -> str:
    """
    Combine product data into one search-optimized string.
    This runs ONCE when you import products, not during search.
    """
    parts = []
    
    # 1. Title (most important)
    if product.get('title'):
        parts.append(product['title'])
    
    # 2. Brand
    if product.get('brand'):
        parts.append(product['brand'])
    
    # 3. Category with variations
    if product.get('category'):
        category_lower = product['category'].lower()
        parts.append(product['category'])
        
        # Better category detection (case-insensitive and more precise)
        if 'men' in category_lower and 'women' not in category_lower:
            parts.append('men male')
        elif 'women' in category_lower:
            parts.append('women female')
    
    # 4. Tags
    if product.get('tags'):
        tags = json.loads(product['tags']) if isinstance(product['tags'], str) else product['tags']
        parts.extend(tags)
    
    # 5. Extract keywords from description dynamically using constants
    if product.get('description'):
        desc_lower = product['description'].lower()
        
        # Extract all keyword types dynamically
        for keyword_list in SEARCH_KEYWORDS.values():
            for keyword in keyword_list:
                if keyword in desc_lower:
                    parts.append(keyword)
    
    # 6. Gender mapping (concise)
    if product.get('gender'):
        gender_map = {
            'M': 'men male',
            'F': 'women female',
            'U': 'unisex'
        }
        parts.append(gender_map.get(product['gender'], ''))
    
    # 7. New searchable attributes
    if product.get('material'):
        parts.append(product['material'])
    if product.get('style'):
        parts.append(product['style'])
    if product.get('color'):
        parts.append(product['color'])
    if product.get('pattern'):
        parts.append(product['pattern'])
    
    return ' '.join(parts).lower()