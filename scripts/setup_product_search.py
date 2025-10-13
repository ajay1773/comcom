#!/usr/bin/env python3
"""
Setup script for Product Search Pipeline

This script:
1. Creates database indexes for optimal search performance
2. Verifies the database schema
3. Tests basic product queries

Run with: python scripts/setup_product_search.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.db.db import db_service


async def create_indexes():
    """Create all necessary database indexes"""
    print("📊 Creating database indexes...")
    
    indexes = [
        # Primary search indexes
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
        "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)",
        "CREATE INDEX IF NOT EXISTS idx_products_price ON products(price)",
        "CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating DESC)",
        "CREATE INDEX IF NOT EXISTS idx_products_stock ON products(stock DESC)",
        "CREATE INDEX IF NOT EXISTS idx_products_availability ON products(availability_status)",
        "CREATE INDEX IF NOT EXISTS idx_products_gender ON products(gender)",
        
        # Composite indexes for common query patterns
        "CREATE INDEX IF NOT EXISTS idx_products_category_price ON products(category, price)",
        "CREATE INDEX IF NOT EXISTS idx_products_category_brand ON products(category, brand)",
        "CREATE INDEX IF NOT EXISTS idx_products_category_rating ON products(category, rating DESC)",
        "CREATE INDEX IF NOT EXISTS idx_products_brand_price ON products(brand, price)",
        
        # Full-text search index (optional)
        "CREATE INDEX IF NOT EXISTS idx_products_title_lower ON products(LOWER(title))",
    ]
    
    for idx_sql in indexes:
        try:
            await db_service.execute_query(idx_sql, None)
            index_name = idx_sql.split("IF NOT EXISTS ")[1].split(" ON")[0]
            print(f"  ✅ Created index: {index_name}")
        except Exception as e:
            print(f"  ❌ Error creating index: {e}")
    
    # Analyze tables for query optimization
    try:
        await db_service.execute_query("ANALYZE products", None)
        print("  ✅ Analyzed products table")
    except Exception as e:
        print(f"  ❌ Error analyzing table: {e}")


async def verify_schema():
    """Verify database schema"""
    print("\n🔍 Verifying database schema...")
    
    # Check if products table exists
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
    result = await db_service.execute_query(query, None)
    
    if result:
        print("  ✅ Products table exists")
        
        # Get column count
        query = "SELECT COUNT(*) FROM pragma_table_info('products')"
        result = await db_service.execute_query(query, None)
        if result:
            col_count = result[0][0]
            print(f"  ✅ Products table has {col_count} columns")
        
        # Get product count
        query = "SELECT COUNT(*) FROM products"
        result = await db_service.execute_query(query, None)
        if result:
            product_count = result[0][0]
            print(f"  ✅ Database contains {product_count} products")
    else:
        print("  ❌ Products table not found!")
        return False
    
    return True


async def test_queries():
    """Test basic product queries"""
    print("\n🧪 Testing product queries...")
    
    from app.services.db.product import product_service
    
    # Test 1: Search by category
    try:
        products = await product_service.get_products({
            "product_category": "smartphones",
            "search_type": "general"
        })
        print(f"  ✅ Category search: Found {len(products)} smartphones")
    except Exception as e:
        print(f"  ❌ Category search failed: {e}")
    
    # Test 2: Search with title
    try:
        products = await product_service.get_products({
            "title": "iPhone",
            "search_type": "specific"
        })
        print(f"  ✅ Title search: Found {len(products)} products matching 'iPhone'")
    except Exception as e:
        print(f"  ❌ Title search failed: {e}")
    
    # Test 3: Search with price filter
    try:
        products = await product_service.get_products({
            "product_category": "laptops",
            "price_max": 2000,
            "search_type": "general"
        })
        print(f"  ✅ Price filter: Found {len(products)} laptops under $2000")
    except Exception as e:
        print(f"  ❌ Price filter failed: {e}")
    
    # Test 4: Search with brand
    try:
        products = await product_service.get_products({
            "brand": "Apple",
            "search_type": "hybrid"
        })
        print(f"  ✅ Brand search: Found {len(products)} Apple products")
    except Exception as e:
        print(f"  ❌ Brand search failed: {e}")


async def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 Product Search Pipeline Setup")
    print("=" * 60)
    
    # Step 1: Create indexes
    await create_indexes()
    
    # Step 2: Verify schema
    schema_ok = await verify_schema()
    if not schema_ok:
        print("\n❌ Schema verification failed. Please check your database.")
        return
    
    # Step 3: Test queries
    await test_queries()
    
    print("\n" + "=" * 60)
    print("✅ Product Search Pipeline Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test the search workflow with: 'show me laptops'")
    print("2. Try specific searches: 'I want an iPhone 14'")
    print("3. Test price filters: 'Nike shoes under $100'")
    print("4. Monitor query performance in logs")


if __name__ == "__main__":
    asyncio.run(main())

