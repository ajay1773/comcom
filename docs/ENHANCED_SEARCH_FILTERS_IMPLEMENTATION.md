# Enhanced Search Filters Implementation Guide

## Quick Implementation: New Product Attribute Filters

Since we just added `material`, `style`, `pattern`, `color` fields to the products table, here's how to add them to search:

### Step 1: Update Entities Model

```python
# app/models/classifier.py

class Entities(BaseModel):
    # ... existing fields ...

    # NEW: Product attribute filters
    colors: list[str] = Field(
        default_factory=list,
        description="Product colors (e.g., ['red', 'blue', 'black'])"
    )

    materials: list[str] = Field(
        default_factory=list,
        description="Product materials (e.g., ['leather', 'cotton', 'polyester'])"
    )

    styles: list[str] = Field(
        default_factory=list,
        description="Product styles (e.g., ['casual', 'formal', 'athletic'])"
    )

    patterns: list[str] = Field(
        default_factory=list,
        description="Product patterns (e.g., ['striped', 'plaid', 'solid'])"
    )

    sizes: list[str] = Field(
        default_factory=list,
        description="Available sizes (e.g., ['M', 'L', 'XL'] or ['8', '9', '10'])"
    )

    # NEW: Discount filter
    min_discount: float | None = Field(
        default=None,
        description="Minimum discount percentage (0-100)",
        ge=0,
        le=100
    )
```

### Step 2: Update Extraction Prompt

```python
# app/graph/workflows/product_search/nodes/extract_search_parameters.py

# Add to system prompt:
"""
### 9. COLOR FILTERS (optional)
Extract color preferences if mentioned as a list.

Examples:
- "red shoes" → colors: ["red"]
- "black or blue shirts" → colors: ["black", "blue"]
- "shoes" → colors: []

### 10. MATERIAL FILTERS (optional)
Extract material preferences if mentioned as a list.

Examples:
- "leather jacket" → materials: ["leather"]
- "cotton or polyester shirts" → materials: ["cotton", "polyester"]
- "shoes" → materials: []

### 11. STYLE FILTERS (optional)
Extract style preferences if mentioned as a list.

Examples:
- "casual shoes" → styles: ["casual"]
- "formal or athletic wear" → styles: ["formal", "athletic"]
- "shirts" → styles: []

### 12. PATTERN FILTERS (optional)
Extract pattern preferences if mentioned as a list.

Examples:
- "striped shirt" → patterns: ["striped"]
- "plaid or checkered" → patterns: ["plaid", "checkered"]
- "solid color shirt" → patterns: ["solid"]

### 13. SIZE FILTERS (optional)
Extract size requirements if mentioned as a list.

Examples:
- "size 10 shoes" → sizes: ["10"]
- "XL or XXL shirt" → sizes: ["XL", "XXL"]
- "medium dress" → sizes: ["M", "Medium"]

### 14. DISCOUNT FILTER (optional)
Extract minimum discount if mentioned.

Examples:
- "products with 20% off" → min_discount: 20
- "50% discount or more" → min_discount: 50
- "on sale" → min_discount: 5
"""
```

### Step 3: Update Database Query

```python
# app/services/db/product.py

async def search_products_fts(self, search_params: Dict[str, Any], limit: int = 20) -> List[Product]:
    # ... existing code ...

    # Apply color filter
    if colors := search_params.get("colors", []):
        if len(colors) > 0:
            color_placeholders = " OR ".join(["LOWER(p.color) LIKE LOWER(?)"] * len(colors))
            filters.append(f"({color_placeholders})")
            query_params.extend([f"%{color}%" for color in colors])

    # Apply material filter
    if materials := search_params.get("materials", []):
        if len(materials) > 0:
            material_placeholders = " OR ".join(["LOWER(p.material) LIKE LOWER(?)"] * len(materials))
            filters.append(f"({material_placeholders})")
            query_params.extend([f"%{mat}%" for mat in materials])

    # Apply style filter
    if styles := search_params.get("styles", []):
        if len(styles) > 0:
            style_placeholders = " OR ".join(["LOWER(p.style) LIKE LOWER(?)"] * len(styles))
            filters.append(f"({style_placeholders})")
            query_params.extend([f"%{style}%" for style in styles])

    # Apply pattern filter
    if patterns := search_params.get("patterns", []):
        if len(patterns) > 0:
            pattern_placeholders = " OR ".join(["LOWER(p.pattern) LIKE LOWER(?)"] * len(patterns))
            filters.append(f"({pattern_placeholders})")
            query_params.extend([f"%{pat}%" for pat in patterns])

    # Apply size filter
    if sizes := search_params.get("sizes", []):
        if len(sizes) > 0:
            # available_sizes is a JSON array, so we search within it
            size_placeholders = " OR ".join(["LOWER(p.available_sizes) LIKE LOWER(?)"] * len(sizes))
            filters.append(f"({size_placeholders})")
            query_params.extend([f'%"{size}"%' for size in sizes])

    # Apply discount filter
    if min_discount := search_params.get("min_discount"):
        filters.append("p.discount_percentage >= ?")
        query_params.append(min_discount)

    # ... rest of existing code ...
```

### Step 4: Update Product Type

```python
# app/graph/workflows/product_search/types.py

class Product(TypedDict):
    # ... existing fields ...
    color: str | None
    material: str | None
    style: str | None
    pattern: str | None
```

### Step 5: Update Row Conversion

```python
# app/services/db/product.py

def _convert_row_to_product(self, row) -> Product:
    # ... existing code ...

    return cast(Product, {
        # ... existing fields ...
        "gender": row[24],
        "material": row[25],
        "style": row[26],
        "pattern": row[27],
        "color": row[28]
    })
```

## Testing Examples

After implementation, test with these queries:

```python
# Color search
"Show me red shoes"
"Black or blue dresses"

# Material search
"Leather jackets"
"Cotton and polyester shirts"

# Style search
"Casual shoes for men"
"Formal wear"

# Pattern search
"Striped shirts"
"Plaid or checkered patterns"

# Size search
"Size 10 shoes"
"XL t-shirts"

# Discount search
"Products with 50% off"
"Items on sale"

# Combined filters
"Red leather casual shoes size 10 under $100"
"Cotton striped shirts XL with 20% discount"
```

## Benefits

1. ✅ More precise search results
2. ✅ Better user experience
3. ✅ Reduced irrelevant results
4. ✅ Supports natural language queries
5. ✅ Easy to implement (uses existing infrastructure)
6. ✅ No performance impact (indexed fields)

## Next Steps

After implementing these filters:

1. Monitor query logs to see which filters are used most
2. Add autocomplete suggestions for common values
3. Implement faceted search to show available options
4. Add "similar items" based on attributes
5. Create filter combinations presets (e.g., "Business Casual", "Athletic Wear")
