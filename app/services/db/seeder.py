from faker import Faker
from typing import Tuple
from app.services.db.db import db_service
import json

# Initialize Faker with consistent seed for reproducible data
fake = Faker()
Faker.seed(12345)

def generate_product() -> Tuple:
    """Generate a single product record using Faker."""

    # Use Faker's providers to generate realistic data
    category = fake.random_element(elements=('clothing', 'shoes', 'accessories', 'bags', 'jewelry'))
    
    # Generate sizes and unit based on category
    if category == 'clothing':
        available_sizes = json.dumps(['XS', 'S', 'M', 'L', 'XL', 'XXL'])
        unit = 'piece'
    elif category == 'shoes':
        available_sizes = json.dumps(['6', '7', '8', '9', '10', '11', '12'])
        unit = 'pair'
    elif category == 'accessories':
        if fake.random_element(['watch', 'belt', 'scarf', 'hat']) in ['watch', 'belt']:
            available_sizes = json.dumps(['S', 'M', 'L'])
        else:
            available_sizes = json.dumps(['One Size'])
        unit = 'piece'
    elif category == 'bags':
        available_sizes = json.dumps(['Small', 'Medium', 'Large'])
        unit = 'piece'
    else:  # jewelry
        available_sizes = json.dumps(['One Size', 'Adjustable'])
        unit = 'piece'

    # Generate product name based on category
    if category == 'clothing':
        product_name = fake.random_element(elements=(
            'T-Shirt', 'Shirt', 'Jeans', 'Dress', 'Sweater', 'Jacket', 'Hoodie',
            f"{fake.word()} Collection {fake.word().title()} Shirt",
            f"{fake.word().title()} Series {fake.word().title()} Pants",
            f"{fake.word().title()} {fake.word().title()} Dress"
        ))
    elif category == 'shoes':
        product_name = fake.random_element(elements=(
            f"{fake.word().title()} {fake.random_element(['Sneakers', 'Boots', 'Loafers', 'Running Shoes'])}",
            f"{fake.word().title()} Collection {fake.word().title()} Shoes"
        ))
    elif category == 'accessories':
        product_name = fake.random_element(elements=(
            f"{fake.word().title()} {fake.random_element(['Watch', 'Belt', 'Scarf', 'Hat', 'Sunglasses'])}",
            f"{fake.word().title()} Series {fake.word().title()} Accessory"
        ))
    elif category == 'bags':
        product_name = fake.random_element(elements=(
            f"{fake.word().title()} {fake.random_element(['Backpack', 'Tote', 'Messenger Bag', 'Handbag'])}",
            f"{fake.word().title()} Collection {fake.word().title()} Bag"
        ))
    else:  # jewelry
        product_name = fake.random_element(elements=(
            f"{fake.word().title()} {fake.random_element(['Necklace', 'Ring', 'Bracelet', 'Earrings'])}",
            f"{fake.word().title()} Collection {fake.word().title()} Jewelry"
        ))

    # Generate price based on category
    price_ranges = {
        'clothing': (20, 200),
        'shoes': (40, 300),
        'accessories': (15, 150),
        'bags': (30, 400),
        'jewelry': (50, 1000)
    }
    price = round(fake.pyfloat(min_value=price_ranges[category][0],
                              max_value=price_ranges[category][1],
                              right_digits=2), 2)

    # Generate other attributes using Faker
    gender = fake.random_element(elements=('M', 'F', 'U'))
    brand = fake.company()  # Use real-looking company names
    material = fake.random_element(elements=(
        'Cotton', 'Leather', 'Denim', 'Silk', 'Wool', 'Polyester', 'Linen',
        fake.word().title()  # Sometimes generate unique materials
    ))
    style = fake.random_element(elements=(
        'Casual', 'Formal', 'Sporty', 'Vintage', 'Modern', 'Classic',
        f"{fake.word().title()} Style"  # Generate unique styles
    ))
    pattern = fake.random_element(elements=(
        'Solid', 'Striped', 'Plaid', 'Floral', 'Polka Dot',
        f"{fake.word().title()} Pattern"  # Generate unique patterns
    ))
    color = fake.color_name()  # Use Faker's color names

    # Create product name with color for better searchability
    full_name = f"{color.title()} {product_name}"

    # Generate image URLs using picsum
    # Using different sizes for different views
    image_id = fake.random_int(min=1, max=1000)  # Picsum has images from 1 to 1000
    images = {
        "thumbnail": f"https://picsum.photos/id/{image_id}/200/200",  # Small thumbnail
        "preview": f"https://picsum.photos/id/{image_id}/400/400",    # Medium preview
        "full": f"https://picsum.photos/id/{image_id}/800/800"        # Full size
    }
    images_json = json.dumps(images)

    return (
        full_name,
        category,
        price,
        gender,
        brand,
        material,
        style,
        pattern,
        color,
        images_json,  # Add images as JSON string
        available_sizes,  # Add available sizes as JSON string
        unit  # Add unit
    )

async def seed_database(num_products: int = 100) -> None:
    """
    Seed the database with generated products.
    Only seeds if the database is empty.
    """
    # Check if database is already seeded
    existing_products = await db_service.execute_query("SELECT COUNT(*) FROM products")
    if existing_products and existing_products[0][0] > 0:
        print("Database already seeded, skipping...")
        return

    # Generate products
    products = [generate_product() for _ in range(num_products)]

    # Create products table with all necessary columns
    await db_service.execute_query("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            price REAL,
            gender TEXT,
            brand TEXT,
            material TEXT,
            style TEXT,
            pattern TEXT,
            color TEXT,
            images TEXT,  -- JSON string containing image URLs
            available_sizes TEXT NOT NULL DEFAULT '[]',  -- JSON string containing available sizes
            unit TEXT NOT NULL DEFAULT 'piece'  -- Unit of measurement
        )
    """)

    # Insert products
    await db_service.execute_query(
        """
        INSERT INTO products (name, category, price, gender, brand, material, style, pattern, color, images, available_sizes, unit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        products
    )

    print(f"Seeded database with {num_products} products")
