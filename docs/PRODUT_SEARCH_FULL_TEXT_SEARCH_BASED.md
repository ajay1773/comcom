# Product Search Pipeline - Full text search based

User Query
↓
┌────────────────────────────────────┐
│ ONE-TIME LLM Call │
│ Extract: keywords + filters │
│ (Simple JSON extraction) │
└────────────────────────────────────┘
↓
┌────────────────────────────────────┐
│ SQLite FTS5 Search │
│ (Built-in full-text search) │
│ - Handles typos automatically │
│ - Ranks by relevance │
│ - Fast and free! │
└────────────────────────────────────┘
↓
┌────────────────────────────────────┐
│ Simple Python Filtering │
│ (Price, rating, stock, etc.) │
└────────────────────────────────────┘
↓
Results (Already ranked by FTS5!)

##📊 Database Schema (Clean & Simple)

```
-- Your existing products table stays EXACTLY as-is
-- Just add ONE column:
ALTER TABLE products ADD COLUMN search_text TEXT;

-- Create FTS5 virtual table (this is the magic!)
CREATE VIRTUAL TABLE products_fts USING fts5(
    product_id UNINDEXED,
    search_text,
    content='products',
    content_rowid='id'
);

-- That's it! No complex attribute tables needed.
```

## Step1: Build Search Text (Run Once)

```
def create_search_text(product: dict) -> str:
    """
    Combine product data into one search-optimized string.
    This runs ONCE when you import products, not during search.
    """
    parts = []

    # 1. Title (most important) - add it twice for weight
    if product.get('title'):
        parts.append(product['title'])
        parts.append(product['title'])  # Repeat for higher weight

    # 2. Brand
    if product.get('brand'):
        parts.append(product['brand'])

    # 3. Category
    if product.get('category'):
        parts.append(product['category'])
        # Add category variations
        if 'mens' in product['category']:
            parts.append('men male')
        if 'womens' in product['category']:
            parts.append('women female')

    # 4. Tags
    if product.get('tags'):
        tags = json.loads(product['tags']) if isinstance(product['tags'], str) else product['tags']
        parts.extend(tags)

    # 5. Extract key terms from description (simple keyword extraction)
    if product.get('description'):
        # Extract color words
        colors = ['red', 'blue', 'black', 'white', 'green', 'yellow', 'pink', 'purple',
                 'brown', 'gray', 'grey', 'orange', 'silver', 'gold']
        desc_lower = product['description'].lower()
        for color in colors:
            if color in desc_lower:
                parts.append(color)

        # Extract material words
        materials = ['leather', 'cotton', 'polyester', 'wool', 'silk', 'denim',
                    'metal', 'plastic', 'wood', 'glass', 'synthetic', 'mesh']
        for material in materials:
            if material in desc_lower:
                parts.append(material)

        # Extract style words
        styles = ['casual', 'formal', 'athletic', 'sports', 'running', 'walking',
                 'vintage', 'modern', 'classic', 'slim', 'regular', 'loose']
        for style in styles:
            if style in desc_lower:
                parts.append(style)

    # 6. Gender mapping
    if product.get('gender'):
        gender_map = {
            'M': 'men mens male man',
            'F': 'women womens female woman',
            'U': 'unisex'
        }
        parts.append(gender_map.get(product['gender'], ''))

    return ' '.join(parts).lower()


async def build_search_index():
    """
    Build the search index for all products.
    Run this once after importing products.
    """
    # Get all products
    products = await db.fetch_all("SELECT * FROM products")

    print(f"Building search index for {len(products)} products...")

    for product in products:
        search_text = create_search_text(product)

        # Update products table
        await db.execute(
            "UPDATE products SET search_text = ? WHERE id = ?",
            search_text, product['id']
        )

        # Insert into FTS5 table
        await db.execute(
            "INSERT INTO products_fts(product_id, search_text) VALUES (?, ?)",
            product['id'], search_text
        )

    print("✅ Search index built successfully!")


# Run this once
if __name__ == "__main__":
    import asyncio
    asyncio.run(build_search_index())

```

## Example Search outputs

```
   # Product: Nike Air Jordan 1 Red And Black
   search_text = "nike air jordan 1 red and black nike air jordan 1 red and black nike mens-shoes men male footwear athletic shoes red black leather men mens male man"

   # Product: Essence Mascara Lash Princess
   search_text = "essence mascara lash princess essence mascara lash princess essence beauty unisex beauty mascara black"
```

## 🔍 Step 2: Simplified LLM Extraction (ONE Call)

```
async def extract_search_params(user_query: str) -> dict:
    """
    Single LLM call to extract search parameters.
    Keep it simple!
    """

    prompt = f"""
Extract search parameters from this query. Return ONLY valid JSON.

Query: "{user_query}"

Extract:
1. keywords: Main search terms (product type, brand, attributes)
2. price_min: Minimum price (if mentioned)
3. price_max: Maximum price (if mentioned)
4. rating_min: Minimum rating (if mentioned)
5. gender: "M" or "F" or null (if mentioned "men", "women", "male", "female")

Examples:

Query: "red shoes for men"
{{"keywords": "red shoes", "gender": "M"}}

Query: "Nike running shoes under 100"
{{"keywords": "Nike running shoes", "price_max": 100}}

Query: "women's dresses"
{{"keywords": "dresses", "gender": "F"}}

Query: "iPhone 14 Pro"
{{"keywords": "iPhone 14 Pro"}}

Query: "laptops under 1000 with good ratings"
{{"keywords": "laptops", "price_max": 1000, "rating_min": 4}}

Now extract from: "{user_query}"

JSON only:
"""

    response = await llm.generate(prompt, temperature=0)
    return json.loads(response)
```

##🚀 Step 3: FTS5 Search with Ranking (No LLM!)

```
async def search_products(user_query: str, limit: int = 20) -> list:
    """
    Main search function using FTS5.
    Only ONE LLM call for extraction!
    """

    # Step 1: Extract parameters (ONE LLM CALL)
    params = await extract_search_params(user_query)

    # Step 2: Build FTS5 query
    keywords = params.get('keywords', user_query)

    # FTS5 automatically handles:
    # - Typos (iphone -> iPhone)
    # - Case insensitivity
    # - Relevance ranking
    # - Partial matches

    query = """
    SELECT
        p.*,
        fts.rank AS relevance_score
    FROM products_fts fts
    JOIN products p ON fts.product_id = p.id
    WHERE products_fts MATCH ?
    """

    query_params = [keywords]

    # Step 3: Add simple filters
    filters = []

    if params.get('gender'):
        filters.append("(p.gender = ? OR p.gender = 'U')")
        query_params.append(params['gender'])

    if params.get('price_min'):
        filters.append("p.price >= ?")
        query_params.append(params['price_min'])

    if params.get('price_max'):
        filters.append("p.price <= ?")
        query_params.append(params['price_max'])

    if params.get('rating_min'):
        filters.append("p.rating >= ?")
        query_params.append(params['rating_min'])

    if filters:
        query += " AND " + " AND ".join(filters)

    # Step 4: Order by FTS5's built-in relevance ranking
    query += " ORDER BY relevance_score DESC LIMIT ?"
    query_params.append(limit)

    # Execute search
    results = await db.fetch_all(query, query_params)

    return results
```

# User query: "red shoes for men"

# Step 1: LLM extraction (1 call)

params = {
"keywords": "red shoes",
"gender": "M"
}

# Step 2: FTS5 search

# Searches products_fts for "red shoes"

# FTS5 AUTOMATICALLY ranks results by relevance:

# - Products with "red" AND "shoes" in search_text rank highest

# - Products with just "red" or just "shoes" rank lower

# - FTS5 uses BM25 algorithm (same as search engines!)

# Step 3: Gender filter

# WHERE (gender = 'M' OR gender = 'U')

# Result: Only red shoes for men! ✅
