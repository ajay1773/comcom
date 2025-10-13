# Enhanced Search Filters - Testing Guide

## ✅ Implementation Complete!

All enhanced search filters have been successfully implemented. Here's how to test them:

---

## 📝 Test Queries

### 1. Color Filter Tests

```
Query: "Show me red shoes"
Expected: Products with color containing "red" and keyword "shoes"

Query: "Black or blue dresses"
Expected: Products with colors "black" OR "blue" and keyword "dresses"

Query: "White Nike sneakers"
Expected: Products with color "white", brand "Nike", keyword "sneakers"
```

### 2. Material Filter Tests

```
Query: "Leather jackets"
Expected: Products with material "leather" and keyword "jackets"

Query: "Cotton or polyester shirts"
Expected: Products with materials "cotton" OR "polyester" and keyword "shirts"

Query: "Wooden furniture"
Expected: Products with material "wood" and category/keyword "furniture"
```

### 3. Style Filter Tests

```
Query: "Casual shoes for men"
Expected: Products with style "casual", keyword "shoes", gender "M"

Query: "Formal wear"
Expected: Products with style "formal"

Query: "Athletic clothing"
Expected: Products with style "athletic" and category/keyword "clothing"
```

### 4. Pattern Filter Tests

```
Query: "Striped shirts"
Expected: Products with pattern "striped" and keyword "shirts"

Query: "Plaid or checkered patterns"
Expected: Products with patterns "plaid" OR "checkered"

Query: "Solid color dress"
Expected: Products with pattern "solid" and keyword "dress"
```

### 5. Size Filter Tests

```
Query: "Size 10 shoes"
Expected: Products with size "10" in available_sizes and keyword "shoes"

Query: "XL or XXL t-shirts"
Expected: Products with sizes "XL" OR "XXL" and keyword "t-shirts"

Query: "Large shirts"
Expected: Products with size "L" or "Large" and keyword "shirts"
```

### 6. Discount Filter Tests

```
Query: "Products with 20% off"
Expected: Products with discount_percentage >= 20

Query: "Items on sale"
Expected: Products with discount_percentage >= 5

Query: "Clearance items"
Expected: Products with discount_percentage >= 30
```

### 7. Combined Filter Tests (Most Important!)

```
Query: "Red leather casual shoes size 10 under $100"
Expected: Products matching ALL of:
- Color: red
- Material: leather
- Style: casual
- Keyword: shoes
- Size: 10
- Price: <= 100

Query: "Cotton striped shirts XL with 20% discount"
Expected: Products matching ALL of:
- Material: cotton
- Pattern: striped
- Keyword: shirts
- Size: XL
- Discount: >= 20%

Query: "Black formal shoes for men under $150"
Expected: Products matching ALL of:
- Color: black
- Style: formal
- Keyword: shoes
- Gender: M
- Price: <= 150
```

---

## 🧪 API Testing Examples

### Using cURL:

```bash
# Test color filter
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me red leather shoes",
    "conversation_id": "test-123"
  }'

# Test combined filters
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cotton shirts XL with 30% discount",
    "conversation_id": "test-456"
  }'
```

### Using Python:

```python
import asyncio
from app.services.db.product import product_service

async def test_enhanced_filters():
    # Test 1: Color filter
    results = await product_service.search_products_fts({
        "keywords": "shoes",
        "colors": ["red"],
        "in_stock_only": True
    }, limit=10)
    print(f"Red shoes: {len(results)} results")

    # Test 2: Material + Style
    results = await product_service.search_products_fts({
        "keywords": "shirts",
        "materials": ["cotton"],
        "styles": ["casual"],
        "in_stock_only": True
    }, limit=10)
    print(f"Cotton casual shirts: {len(results)} results")

    # Test 3: Size filter
    results = await product_service.search_products_fts({
        "keywords": "shoes",
        "sizes": ["10"],
        "in_stock_only": True
    }, limit=10)
    print(f"Size 10 shoes: {len(results)} results")

    # Test 4: Discount filter
    results = await product_service.search_products_fts({
        "keywords": "",
        "min_discount": 20,
        "in_stock_only": True
    }, limit=10)
    print(f"Items with 20%+ discount: {len(results)} results")

    # Test 5: Combined filters
    results = await product_service.search_products_fts({
        "keywords": "shoes",
        "colors": ["black"],
        "materials": ["leather"],
        "styles": ["formal"],
        "sizes": ["10"],
        "price_max": 200,
        "gender": "M",
        "in_stock_only": True
    }, limit=10)
    print(f"Black leather formal shoes size 10 under $200: {len(results)} results")

# Run tests
asyncio.run(test_enhanced_filters())
```

---

## 🔍 What to Verify

For each test query, verify:

1. ✅ **Correct Parameter Extraction**

   - Check that the LLM extracts all filters correctly
   - Verify the `search_parameters` in state

2. ✅ **Database Query Execution**

   - Check SQL query includes all WHERE clauses
   - Verify parameters are passed correctly

3. ✅ **Result Accuracy**

   - All returned products should match ALL specified filters
   - No products should be returned that don't match

4. ✅ **Performance**

   - Query should execute in < 100ms for most cases
   - FTS5 ranking should prioritize relevant results

5. ✅ **Edge Cases**
   - Empty results (no matches)
   - Multiple values for same filter type
   - Conflicting filters (e.g., "red and blue" for single color field)

---

## 🐛 Debugging Tips

### If filters aren't working:

1. **Check LLM Extraction:**

   ```python
   # Add logging in extract_search_parameters_node
   print(f"Extracted parameters: {state['search_parameters']}")
   ```

2. **Check Database Values:**

   ```sql
   -- See what values exist in the database
   SELECT DISTINCT color FROM products WHERE color IS NOT NULL;
   SELECT DISTINCT material FROM products WHERE material IS NOT NULL;
   SELECT DISTINCT style FROM products WHERE style IS NOT NULL;
   SELECT DISTINCT pattern FROM products WHERE pattern IS NOT NULL;
   ```

3. **Check Query Generation:**

   ```python
   # Add logging in search_products_fts
   print(f"Query: {query}")
   print(f"Params: {query_params}")
   ```

4. **Test Direct SQL:**
   ```sql
   -- Test filters directly in SQLite
   SELECT * FROM products
   WHERE LOWER(color) LIKE '%red%'
   AND LOWER(material) LIKE '%leather%'
   LIMIT 10;
   ```

---

## 📊 Expected Behavior

### Case Insensitive Matching

- "Red" matches "red", "RED", "Red"
- "Leather" matches "leather", "LEATHER", "Leather/Wood"

### Partial Matching for Attributes

- Color "Red" matches "Red/Black", "Red/Green"
- Material "Cotton" matches "Cotton Blend", "100% Cotton"

### Multiple Values (OR Logic)

- colors: ["red", "blue"] → matches products with EITHER red OR blue
- materials: ["cotton", "polyester"] → matches EITHER cotton OR polyester

### Multiple Filters (AND Logic)

- color: red + material: leather → matches products with BOTH red AND leather

### Size Matching

- Searches within JSON array: ["S", "M", "L"]
- "M" matches any product with "M" in available_sizes

### Discount Filter

- min_discount: 20 → only products with discount_percentage >= 20
- Works even if keyword is empty (shows all discounted items)

---

## ✨ New Search Capabilities Summary

### Before Enhancement:

- ✅ Keywords (FTS5)
- ✅ Price range
- ✅ Rating
- ✅ Gender
- ✅ Brands
- ✅ Categories
- ✅ Sort options
- ✅ Stock filter

### After Enhancement (NEW):

- ⭐ **Colors** - multi-value filter
- ⭐ **Materials** - multi-value filter
- ⭐ **Styles** - multi-value filter
- ⭐ **Patterns** - multi-value filter
- ⭐ **Sizes** - multi-value filter
- ⭐ **Minimum Discount** - percentage-based

### Total Search Parameters: **14 filters + 1 sort option**

---

## 🚀 Next Steps

After testing and validation:

1. **Monitor Usage:**

   - Track which filters are used most frequently
   - Identify common filter combinations

2. **Optimize Performance:**

   - Add indexes for frequently filtered columns
   - Consider caching popular filter combinations

3. **Enhance UX:**

   - Add filter UI in frontend
   - Show available filter options (faceted search)
   - Display active filters clearly

4. **Add Analytics:**

   - Track filter usage patterns
   - Identify gaps in product attributes
   - Measure search success rates

5. **Future Enhancements:**
   - Autocomplete for filter values
   - Smart suggestions based on partial queries
   - "Save filter" functionality
   - Filter presets (e.g., "Budget Casual", "Premium Formal")

---

## 📝 Notes

- All filters support case-insensitive matching
- Filters use LIKE with wildcards for flexible matching
- Empty filter arrays are ignored (no filtering applied)
- Null values in database are handled gracefully
- Performance should remain fast due to FTS5 indexing

---

**Implementation Date:** 2025-10-11
**Status:** ✅ Complete and Ready for Testing
