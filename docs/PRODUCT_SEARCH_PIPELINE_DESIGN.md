# Product Search Pipeline Design Document

## 1. Data Structure Analysis

### 1.1 Products Table Schema

Based on the CSV data analysis, the products table contains the following key fields:

```
- id: Unique product identifier
- title: Product name (Primary search field)
- description: Detailed product description (Secondary search field)
- category: Single category classification (e.g., "beauty", "laptops", "mens-shirts")
- tags: JSON array of tags (e.g., ["beauty", "mascara"], ["laptops", "apple"])
- brand: Brand name (e.g., "Apple", "Nike", "Essence")
- price: Product price (decimal)
- rating: Product rating (0-5 scale)
- stock: Available stock quantity
- availability_status: Stock status ("In Stock", "Low Stock", "Out of Stock")
- gender: Target gender (M, F, U for unisex)
- available_sizes: JSON array of sizes
```

### 1.2 Field Interrelationships

**Title → Brand → Category → Tags → Description**

1. **Title** (Most Specific)

   - Contains the full product name
   - Often includes brand name
   - Examples: "Apple MacBook Pro 14 Inch Space Grey", "Nike Air Jordan 1 Red And Black"

2. **Brand** (Specific Entity)

   - Extracted from title or standalone field
   - Used for brand-specific searches
   - Examples: "Apple", "Nike", "Rolex"

3. **Category** (Broad Classification)

   - Single, high-level classification
   - 25+ categories in the system
   - Examples: "laptops", "mens-shoes", "beauty"

4. **Tags** (Multi-level Classification)

   - Array of 1-5 tags per product
   - Usually includes the category as one tag
   - Includes sub-categories and attributes
   - Examples: ["laptops", "apple"], ["beauty", "mascara"], ["footwear", "athletic shoes"]

5. **Description** (Most General)
   - Full-text description with features, benefits, and details
   - Contains semantic information about the product
   - May include synonyms and related terms

### 1.3 Key Observations

1. **Category-Tag Relationship**: Tags often include the category (e.g., if category is "beauty", tags will have "beauty" as one element)

2. **Title-Brand Overlap**: Brand names frequently appear in the title field (e.g., "Apple MacBook Pro")

3. **Hierarchical Nature**:

   ```
   Category (broad) → Tags (medium) → Title (specific)
   "laptops" → ["laptops", "apple"] → "Apple MacBook Pro 14 Inch Space Grey"
   ```

4. **Search Implications**:
   - General searches (e.g., "smartphones") should match category/tags
   - Specific searches (e.g., "iPhone 14") should prioritize title
   - Fuzzy searches need to check multiple fields with different weights

---

## 2. Current Implementation Analysis

### 2.1 Current Pipeline

```
User Query → LLM Parameter Extraction → SQL Query Building → Results Return
```

**Strengths:**

- ✅ Uses LLM for intelligent parameter extraction
- ✅ Handles multiple search parameters (category, brand, price, etc.)
- ✅ Case-insensitive search
- ✅ Searches across multiple fields (title, tags, description)

**Weaknesses:**

- ❌ No relevance scoring or ranking
- ❌ OR conditions can return too many irrelevant results
- ❌ No fuzzy matching for typos
- ❌ No distinction between exact and partial matches
- ❌ Results are unordered (random order from database)
- ❌ No handling for no-results scenarios
- ❌ Equal weight to title, tags, and description matches

### 2.2 Current SQL Query Pattern

```sql
SELECT * FROM products
WHERE (category = ?)
  AND (LOWER(title) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(description) LIKE ?)
  AND (LOWER(tags) LIKE ? OR LOWER(title) LIKE ? OR LOWER(description) LIKE ?)
  -- ... more tag conditions
```

**Problems:**

1. All matches are treated equally (title match = description match)
2. No result ordering or scoring
3. Tag searches are too broad (OR across all fields)
4. No handling of partial matches vs. exact matches

---

## 3. Proposed Enhanced Search Pipeline

### 3.1 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Query Input                             │
└────────────────────────────────┬────────────────────────────────────┘
                                  │
                ┌─────────────────▼──────────────────┐
                │  Step 1: Query Classification      │
                │  (Determine search type)           │
                │  - Specific Product Search         │
                │  - General Category Search         │
                │  - Hybrid Search                   │
                └─────────────────┬──────────────────┘
                                  │
                ┌─────────────────▼──────────────────┐
                │  Step 2: Parameter Extraction      │
                │  (LLM-based structured extraction) │
                │  - Category                        │
                │  - Title keywords                  │
                │  - Tags                            │
                │  - Brand                           │
                │  - Filters (price, rating, etc.)   │
                └─────────────────┬──────────────────┘
                                  │
                ┌─────────────────▼──────────────────┐
                │  Step 3: Multi-Stage Search        │
                │                                     │
                │  Stage 1: Candidate Retrieval      │
                │  ├─ Exact Title Match              │
                │  ├─ Category Match                 │
                │  └─ Tag Match                      │
                │                                     │
                │  Stage 2: Scoring & Ranking        │
                │  ├─ Field-weighted scoring         │
                │  ├─ Term frequency                 │
                │  └─ Match type (exact/partial)     │
                │                                     │
                │  Stage 3: Filtering                │
                │  └─ Apply filters (price, etc.)    │
                └─────────────────┬──────────────────┘
                                  │
                ┌─────────────────▼──────────────────┐
                │  Step 4: Result Ranking            │
                │  - Sort by relevance score         │
                │  - Apply business rules            │
                │  - Limit results                   │
                └─────────────────┬──────────────────┘
                                  │
                ┌─────────────────▼──────────────────┐
                │  Step 5: Fallback Handling         │
                │  - If results < threshold          │
                │  - Relaxed search                  │
                │  - Suggestions generation          │
                └─────────────────┬──────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │  Return Results  │
                        └──────────────────┘
```

### 3.2 Search Type Classification

**Type 1: Specific Product Search**

- User mentions a specific product name or model
- Examples: "iPhone 14", "MacBook Pro", "Nike Air Jordan"
- Strategy: Prioritize exact title matches, then partial title matches

**Type 2: General Category Search**

- User asks for a category or product type
- Examples: "smartphones", "laptops", "beauty products", "men's shoes"
- Strategy: Match category first, then use tags for filtering

**Type 3: Hybrid Search**

- Combination of specific and general
- Examples: "Apple laptops", "Nike running shoes", "red dresses"
- Strategy: Match category + brand/attributes, score by relevance

---

## 4. Detailed Implementation Strategy

### 4.1 Step 1: Query Classification (Enhanced LLM Prompt)

Add search type classification to the extraction prompt:

```python
{
    "search_type": "specific" | "general" | "hybrid",
    "confidence": 0.0-1.0,
    "primary_intent": "product_name" | "category" | "brand_category",
    ...existing parameters
}
```

### 4.2 Step 2: Enhanced Parameter Extraction

**Current Parameters:**

- product_category
- title
- tags
- brand
- price_min, price_max
- rating_min
- gender

**Proposed Additions:**

- `search_type`: Type of search (specific/general/hybrid)
- `search_terms`: Array of key terms for scoring
- `exact_match_required`: Boolean flag for exact matching
- `title_priority`: Weight for title matching (0.0-1.0)

### 4.3 Step 3: Multi-Stage Search with Scoring

#### Stage 1: Candidate Retrieval

Build multiple SQL queries based on search type:

**For Specific Searches:**

```sql
-- Stage 1a: Exact title match
SELECT *, 100 as score FROM products
WHERE LOWER(title) = LOWER(?)

UNION

-- Stage 1b: Title starts with
SELECT *, 80 as score FROM products
WHERE LOWER(title) LIKE LOWER(?) || '%'

UNION

-- Stage 1c: Title contains
SELECT *, 60 as score FROM products
WHERE LOWER(title) LIKE '%' || LOWER(?) || '%'
  AND LOWER(title) != LOWER(?)
```

**For General Searches:**

```sql
-- Stage 1a: Exact category match
SELECT *, 50 as score FROM products
WHERE category = ?

UNION

-- Stage 1b: Tag match
SELECT *, 40 as score FROM products
WHERE tags LIKE ?
```

#### Stage 2: Relevance Scoring Algorithm

**Scoring Formula:**

```
Total Score = (Title Score × 0.5) +
              (Tag Score × 0.2) +
              (Description Score × 0.1) +
              (Category Score × 0.15) +
              (Brand Score × 0.05)
```

**Field Scoring Rules:**

1. **Title Score (Weight: 0.5)**

   - Exact match: 100 points
   - Starts with: 80 points
   - Contains (word boundary): 60 points
   - Contains (partial): 40 points
   - Multiple term matches: +10 points per additional term

2. **Category Score (Weight: 0.15)**

   - Exact match: 100 points
   - No match: 0 points

3. **Tag Score (Weight: 0.2)**

   - Each tag match: 20 points (max 100)
   - Exact tag match: +10 bonus

4. **Description Score (Weight: 0.1)**

   - Contains all search terms: 100 points
   - Contains some terms: (matched_terms / total_terms) × 100

5. **Brand Score (Weight: 0.05)**
   - Exact brand match: 100 points
   - No match: 0 points

**Bonus Modifiers:**

- High rating (>4.5): +5 points
- In stock: +5 points
- Popular (high sales): +10 points (if we track this)

### 4.4 Step 4: Advanced Filtering

Apply filters after scoring to maintain relevance:

```python
def apply_filters(products, filters):
    filtered = products

    # Price range
    if filters.get('price_min'):
        filtered = [p for p in filtered if p['price'] >= filters['price_min']]
    if filters.get('price_max'):
        filtered = [p for p in filtered if p['price'] <= filters['price_max']]

    # Rating
    if filters.get('rating_min'):
        filtered = [p for p in filtered if p['rating'] >= filters['rating_min']]

    # Availability
    if filters.get('availability_status'):
        filtered = [p for p in filtered if p['availability_status'] == filters['availability_status']]

    # Gender
    if filters.get('gender'):
        gender_code = filters['gender'][0].upper()
        filtered = [p for p in filtered if p['gender'] in [gender_code, 'U']]

    return filtered
```

### 4.5 Step 5: Fallback & Suggestion Strategies

**Fallback Scenarios:**

1. **No Results Found**

   - Relax filters (remove price, rating constraints)
   - Try category-only search
   - Use tags for broader search
   - Generate "Did you mean?" suggestions

2. **Too Few Results (< 3)**

   - Expand search to related categories
   - Include similar brands
   - Show "Customers also viewed" products

3. **Too Many Results (> 100)**
   - Apply stricter matching criteria
   - Increase title weight
   - Show top 20 by score + filters

**Suggestion Generation:**

```python
async def generate_suggestions(search_params):
    suggestions = []

    # Category suggestions
    if not search_params.get('product_category'):
        categories = await get_popular_categories()
        suggestions.append({
            "type": "category",
            "text": "Try browsing by category",
            "options": categories
        })

    # Brand suggestions (if typo detected)
    if search_params.get('brand'):
        similar_brands = await find_similar_brands(search_params['brand'])
        if similar_brands:
            suggestions.append({
                "type": "brand",
                "text": "Did you mean?",
                "options": similar_brands
            })

    # Price range suggestions
    if len(results) == 0 and search_params.get('price_max'):
        suggestions.append({
            "type": "price",
            "text": "Try expanding your budget",
            "action": "remove_price_filter"
        })

    return suggestions
```

---

## 5. Implementation Approach: Two-Phase Strategy

### Phase 1: SQL-Based Scoring (Recommended for MVP)

**Advantages:**

- ✅ Works with existing SQLite database
- ✅ No additional dependencies
- ✅ Fast for small-to-medium datasets (<100K products)
- ✅ Can implement immediately

**Implementation:**

```python
async def search_products_with_scoring(search_params):
    search_type = search_params.get('search_type', 'general')

    # Build base query with scoring
    if search_type == 'specific':
        query = """
        SELECT *,
            (CASE
                WHEN LOWER(title) = LOWER(?) THEN 100
                WHEN LOWER(title) LIKE LOWER(?) || '%' THEN 80
                WHEN LOWER(title) LIKE '%' || LOWER(?) || '%' THEN 60
                ELSE 0
            END) * 0.5 +
            (CASE
                WHEN category = ? THEN 100
                ELSE 0
            END) * 0.15 +
            (CASE
                WHEN tags LIKE '%' || ? || '%' THEN 60
                ELSE 0
            END) * 0.2 +
            (CASE
                WHEN LOWER(brand) = LOWER(?) THEN 100
                ELSE 0
            END) * 0.05 +
            (CASE
                WHEN LOWER(description) LIKE '%' || LOWER(?) || '%' THEN 50
                ELSE 0
            END) * 0.1
        AS relevance_score
        FROM products
        WHERE relevance_score > 0
        ORDER BY relevance_score DESC, rating DESC
        LIMIT 20
        """
    else:  # general search
        query = """
        SELECT *,
            (CASE
                WHEN category = ? THEN 100
                ELSE 0
            END) * 0.4 +
            (CASE
                WHEN tags LIKE '%' || ? || '%' THEN 80
                ELSE 0
            END) * 0.3 +
            (CASE
                WHEN LOWER(title) LIKE '%' || LOWER(?) || '%' THEN 60
                ELSE 0
            END) * 0.2 +
            (CASE
                WHEN LOWER(description) LIKE '%' || LOWER(?) || '%' THEN 40
                ELSE 0
            END) * 0.1
        AS relevance_score
        FROM products
        WHERE relevance_score > 0
        ORDER BY relevance_score DESC, rating DESC
        LIMIT 20
        """

    results = await db_service.execute_query(query, params)
    return results
```

### Phase 2: Full-Text Search (Future Enhancement)

**When to Consider:**

- Dataset grows beyond 100K products
- Need fuzzy matching for typos
- Want semantic search capabilities

**Options:**

1. **SQLite FTS5** (Full-Text Search)

   ```sql
   CREATE VIRTUAL TABLE products_fts USING fts5(
       title, description, tags, brand,
       content=products,
       tokenize='porter unicode61'
   );
   ```

2. **Elasticsearch** (Advanced)

   - Best for large-scale search
   - Fuzzy matching built-in
   - Powerful scoring algorithms

3. **Embeddings + Vector Search** (AI-Enhanced)
   - Use for semantic search
   - Understand intent beyond keywords
   - Requires vector database (e.g., Pinecone, Qdrant)

---

## 6. Testing Strategy

### 6.1 Test Cases

**Specific Product Searches:**

- ✅ "iPhone 14" → Should return iPhone 14 products first
- ✅ "MacBook Pro" → Should prioritize MacBook Pro models
- ✅ "Nike Air Jordan" → Should match exact product

**General Category Searches:**

- ✅ "smartphones" → Should return all phones
- ✅ "laptops" → Should return all laptops
- ✅ "beauty products" → Should return beauty category items

**Hybrid Searches:**

- ✅ "Apple laptops" → MacBook products
- ✅ "Nike running shoes" → Nike shoes in sports category
- ✅ "red dress" → Dresses filtered by color attribute

**Fuzzy Searches:**

- ✅ "iphone" (lowercase) → Should match "iPhone"
- ✅ "macbok" (typo) → Future: Should suggest "MacBook"
- ✅ "smartfone" (typo) → Future: Should match "smartphone"

**Edge Cases:**

- ✅ Empty query → Return popular/featured products
- ✅ Very broad query ("show me products") → Return curated list
- ✅ No results → Show suggestions and related categories
- ✅ Too many filters → Relax least important filters

### 6.2 Metrics to Track

1. **Search Accuracy**

   - Top-1 accuracy: % of times the #1 result is relevant
   - Top-5 accuracy: % of times a relevant result is in top 5

2. **Search Performance**

   - Average query time
   - 95th percentile query time

3. **User Satisfaction**
   - Click-through rate on results
   - Zero-result rate
   - Filter usage rate

---

## 7. Recommended Implementation Plan

### Week 1: Foundation

1. ✅ Add search type classification to LLM extraction
2. ✅ Implement SQL-based scoring queries
3. ✅ Update `product_service.py` with new search methods

### Week 2: Scoring & Ranking

1. ✅ Implement weighted scoring algorithm
2. ✅ Add result ranking logic
3. ✅ Test with various query types

### Week 3: Fallback & Polish

1. ✅ Implement fallback strategies
2. ✅ Add suggestion generation
3. ✅ Handle edge cases

### Week 4: Testing & Optimization

1. ✅ Performance testing
2. ✅ Query optimization
3. ✅ A/B testing with users

### Future Enhancements

- SQLite FTS5 for fuzzy matching
- Caching layer for common queries
- Product popularity tracking
- Personalized search results
- Visual search capabilities

---

## 8. Example Queries & Expected Behavior

### Example 1: Specific Product Search

**Query:** "I want an iPhone 14"

**Extraction:**

```json
{
  "search_type": "specific",
  "title": "iPhone 14",
  "product_category": "smartphones",
  "tags": ["electronics", "apple", "smartphone"],
  "brand": "Apple"
}
```

**Expected Results (Ordered by Relevance):**

1. iPhone 14 Pro Max (95 score - exact title match)
2. iPhone 14 Pro (92 score - exact title match)
3. iPhone 14 (90 score - exact match)
4. iPhone 13 (45 score - similar title)

---

### Example 2: General Category Search

**Query:** "Show me laptops"

**Extraction:**

```json
{
  "search_type": "general",
  "product_category": "laptops",
  "tags": ["laptops", "computers", "electronics"]
}
```

**Expected Results:**

- All products in "laptops" category
- Ordered by: relevance score → rating → price

---

### Example 3: Hybrid Search

**Query:** "Nike running shoes under $100"

**Extraction:**

```json
{
  "search_type": "hybrid",
  "title": "Running Shoes",
  "product_category": "mens-shoes",
  "tags": ["shoes", "running", "athletic", "footwear"],
  "brand": "Nike",
  "price_max": 100
}
```

**Expected Results:**

1. Nike running shoes < $100
2. Ordered by relevance (brand match + category + price filter)

---

## 9. Summary & Recommendations

### Key Improvements Over Current Implementation

1. **Relevance Scoring**: Results are now ranked by relevance, not random
2. **Search Type Classification**: Different strategies for specific vs. general searches
3. **Multi-field Weighting**: Title matches weighted higher than description matches
4. **Fallback Strategies**: Handle no-results and low-results scenarios
5. **Better User Experience**: Suggestions and "Did you mean?" functionality

### Immediate Actions

✅ **Start with Phase 1** (SQL-based scoring)

- Lowest friction to implement
- Works with existing infrastructure
- Provides immediate improvements

✅ **Track Metrics**

- Zero-result rate
- Top-5 accuracy
- Query performance

✅ **Iterate Based on Data**

- Monitor common query patterns
- Identify failure cases
- Adjust scoring weights

### Long-term Vision

- Transition to FTS5 or Elasticsearch for scalability
- Add semantic search with embeddings
- Implement personalized search results
- A/B test different scoring algorithms

---

**Document Version:** 1.0  
**Date:** October 5, 2025  
**Status:** Proposed for Review
