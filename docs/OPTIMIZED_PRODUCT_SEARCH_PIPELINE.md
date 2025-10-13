# Optimized Product Search Pipeline Design

## Performance-First Architecture with Minimal LLM Usage

**Goal:** Achieve <100ms search response time while reducing LLM calls by 70-80%

---

## 1. Performance Optimization Strategy

### 1.1 The Problem with Current Approach

**Current Pipeline:**

```
Every Query → LLM Call (500-2000ms) → SQL Query (10-50ms) → Results
```

**Cost Analysis:**

- ⚠️ **LLM call on EVERY search**: 500-2000ms latency
- ⚠️ **No caching**: Repeat queries call LLM again
- ⚠️ **API costs**: $0.001-0.01 per query (adds up at scale)
- ⚠️ **Sequential processing**: No parallelization

---

## 2. Optimized Pipeline Architecture

### 2.1 Three-Tier Search Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query Input                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
      ┌──────────────▼───────────────┐
      │   TIER 1: Fast Path          │  <--- 60-70% of queries
      │   Pattern Matching           │       (0 LLM calls)
      │   - Regex patterns           │       10-50ms response
      │   - Keyword lookup           │
      │   - Common query cache       │
      └──────────┬───────────────────┘
                 │
                 │ Pattern match failed?
                 │
      ┌──────────▼───────────────────┐
      │   TIER 2: Hybrid Path        │  <--- 20-30% of queries
      │   Smart Preprocessing        │       (0 LLM calls)
      │   - NLP lite (spaCy/nltk)    │       50-100ms response
      │   - Rules engine             │
      │   - Fuzzy matching           │
      └──────────┬───────────────────┘
                 │
                 │ Still ambiguous?
                 │
      ┌──────────▼───────────────────┐
      │   TIER 3: LLM Path           │  <--- 5-15% of queries
      │   Full LLM Extraction        │       (1 LLM call)
      │   - Complex queries          │       500-2000ms response
      │   - Ambiguous intent         │
      │   + Cache result             │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │   Optimized SQL Query        │
      │   - Single query with CTE    │
      │   - Indexed fields           │
      │   - Pre-computed scores      │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │   Cached Results             │
      │   - Redis/Memory cache       │
      │   - 5-15 min TTL             │
      └──────────────────────────────┘
```

### 2.2 Expected Performance Gains

| Metric                | Before  | After      | Improvement            |
| --------------------- | ------- | ---------- | ---------------------- |
| Avg Response Time     | 800ms   | <100ms     | **8x faster**          |
| LLM Call Rate         | 100%    | 10-15%     | **85% reduction**      |
| Cache Hit Rate        | 0%      | 40-60%     | **New capability**     |
| Concurrent Queries    | Limited | High       | **Better scalability** |
| Cost per 1000 queries | $5-10   | $0.50-1.50 | **80-90% cheaper**     |

---

## 3. TIER 1: Fast Path (Pattern Matching)

### 3.1 Pattern-Based Query Classification

**Goal:** Instantly classify and extract parameters for common patterns (NO LLM)

```python
import re
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class QuickSearchParams:
    """Fast extraction result"""
    matched: bool
    confidence: float
    category: Optional[str] = None
    title: Optional[str] = None
    brand: Optional[str] = None
    tags: List[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    search_type: str = "general"

class FastPathExtractor:
    """Zero-LLM parameter extraction for common queries"""

    def __init__(self):
        # Pre-compile regex patterns for speed
        self.patterns = self._compile_patterns()
        self.category_map = self._load_category_map()
        self.brand_list = self._load_brand_list()

    def _compile_patterns(self):
        """Compile all regex patterns once at initialization"""
        return {
            # Specific product patterns
            'iphone': re.compile(r'\biphone\s*(\d+)?\s*(pro|max|mini|plus)?\b', re.IGNORECASE),
            'macbook': re.compile(r'\bmacbook\s*(air|pro)?\s*(\d+)?\s*inch?\b', re.IGNORECASE),
            'ipad': re.compile(r'\bipad\s*(air|pro|mini)?\b', re.IGNORECASE),
            'samsung': re.compile(r'\bsamsung\s*galaxy\s*(s|note|a|z)?(\d+)?\b', re.IGNORECASE),
            'nike': re.compile(r'\bnike\s+(air|jordan|max|dunk|blazer|cortez)\b', re.IGNORECASE),
            'rolex': re.compile(r'\brolex\s+(submariner|datejust|daytona|oyster)\b', re.IGNORECASE),

            # Category patterns
            'category_direct': re.compile(
                r'\b(smartphones?|laptops?|tablets?|furniture|beauty|fragrances?|'
                r'groceries|shoes|watches|bags|jewelry|sunglasses)\b',
                re.IGNORECASE
            ),

            # Gendered product patterns
            'mens': re.compile(r'\b(men\'?s|mens|for men|male)\s+(\w+)\b', re.IGNORECASE),
            'womens': re.compile(r'\b(women\'?s|womens|ladies|female|for women)\s+(\w+)\b', re.IGNORECASE),

            # Price patterns
            'price_under': re.compile(r'\bunder\s*\$?(\d+)\b', re.IGNORECASE),
            'price_below': re.compile(r'\bbelow\s*\$?(\d+)\b', re.IGNORECASE),
            'price_above': re.compile(r'\babove\s*\$?(\d+)\b', re.IGNORECASE),
            'price_range': re.compile(r'\$?(\d+)\s*(?:to|-|and)\s*\$?(\d+)\b', re.IGNORECASE),

            # Simple search patterns
            'show_me': re.compile(r'\b(?:show|find|get|search)\s+(?:me\s+)?(\w+)\b', re.IGNORECASE),
            'looking_for': re.compile(r'\blooking\s+for\s+(?:a|an|some)?\s*(\w+)\b', re.IGNORECASE),
            'want': re.compile(r'\b(?:want|need)\s+(?:a|an|some)?\s*(\w+)\b', re.IGNORECASE),
        }

    def _load_category_map(self) -> Dict[str, str]:
        """Map common terms to categories"""
        return {
            # Direct mappings
            'phone': 'smartphones',
            'smartphone': 'smartphones',
            'mobile': 'smartphones',
            'laptop': 'laptops',
            'computer': 'laptops',
            'notebook': 'laptops',
            'tablet': 'tablets',
            'ipad': 'tablets',
            'furniture': 'furniture',
            'sofa': 'furniture',
            'chair': 'furniture',
            'table': 'furniture',
            'bed': 'furniture',
            'makeup': 'beauty',
            'cosmetics': 'beauty',
            'beauty': 'beauty',
            'perfume': 'fragrances',
            'fragrance': 'fragrances',
            'cologne': 'fragrances',
            'food': 'groceries',
            'groceries': 'groceries',
            'snacks': 'groceries',
            'shoes': 'mens-shoes',  # Default to mens, can be overridden
            'sneakers': 'mens-shoes',
            'watch': 'mens-watches',
            'watches': 'mens-watches',
            'bag': 'womens-bags',
            'handbag': 'womens-bags',
            'purse': 'womens-bags',
            'jewelry': 'womens-jewellery',
            'jewellery': 'womens-jewellery',
            'sunglasses': 'sunglasses',
            'shades': 'sunglasses',
            'dress': 'womens-dresses',
            'dresses': 'womens-dresses',
            'shirt': 'mens-shirts',
            'shirts': 'mens-shirts',
        }

    def _load_brand_list(self) -> List[str]:
        """Load known brands for quick matching"""
        return [
            'Apple', 'Samsung', 'Google', 'OnePlus', 'Xiaomi',
            'Nike', 'Adidas', 'Puma', 'Reebok', 'New Balance',
            'Rolex', 'Omega', 'Tag Heuer', 'Seiko', 'Casio',
            'Dell', 'HP', 'Lenovo', 'Asus', 'Acer',
            'Gucci', 'Prada', 'Louis Vuitton', 'Chanel', 'Dior',
            'Calvin Klein', 'Tommy Hilfiger', 'Ralph Lauren',
        ]

    async def extract(self, query: str) -> QuickSearchParams:
        """
        Fast parameter extraction using pattern matching.
        Returns matched=True if confident, False if needs LLM.
        """
        query_lower = query.lower().strip()
        result = QuickSearchParams(matched=False, confidence=0.0, tags=[])

        # Empty query - fast fail
        if not query or len(query) < 2:
            return result

        # Check for specific product patterns (HIGH CONFIDENCE)
        if specific_match := self._check_specific_products(query_lower):
            result.matched = True
            result.confidence = 0.95
            result.update(specific_match)
            return result

        # Check for category patterns (MEDIUM-HIGH CONFIDENCE)
        if category_match := self._check_category_patterns(query_lower):
            result.matched = True
            result.confidence = 0.85
            result.update(category_match)
            return result

        # Check for simple search patterns (MEDIUM CONFIDENCE)
        if simple_match := self._check_simple_patterns(query_lower):
            result.matched = True
            result.confidence = 0.75
            result.update(simple_match)
            return result

        # If we got here, pattern matching failed - need LLM
        return result

    def _check_specific_products(self, query: str) -> Optional[Dict]:
        """Check for specific product mentions like 'iPhone 14'"""

        # iPhone patterns
        if match := self.patterns['iphone'].search(query):
            model = match.group(1) or ""
            variant = match.group(2) or ""
            title = f"iPhone {model} {variant}".strip()
            return {
                'category': 'smartphones',
                'brand': 'Apple',
                'title': title,
                'tags': ['smartphones', 'apple', 'electronics'],
                'search_type': 'specific'
            }

        # MacBook patterns
        if match := self.patterns['macbook'].search(query):
            variant = match.group(1) or ""
            size = match.group(2) or ""
            title = f"MacBook {variant} {size}".strip()
            return {
                'category': 'laptops',
                'brand': 'Apple',
                'title': title,
                'tags': ['laptops', 'apple', 'computers'],
                'search_type': 'specific'
            }

        # Samsung patterns
        if match := self.patterns['samsung'].search(query):
            series = match.group(1) or ""
            model = match.group(2) or ""
            title = f"Samsung Galaxy {series}{model}".strip()
            return {
                'category': 'smartphones',
                'brand': 'Samsung',
                'title': title,
                'tags': ['smartphones', 'samsung', 'android'],
                'search_type': 'specific'
            }

        # Nike patterns
        if match := self.patterns['nike'].search(query):
            line = match.group(1)
            return {
                'category': 'mens-shoes',
                'brand': 'Nike',
                'title': f"Nike {line}",
                'tags': ['shoes', 'nike', 'footwear', 'athletic'],
                'search_type': 'specific'
            }

        # Rolex patterns
        if match := self.patterns['rolex'].search(query):
            model = match.group(1)
            return {
                'category': 'mens-watches',
                'brand': 'Rolex',
                'title': f"Rolex {model}",
                'tags': ['watches', 'luxury', 'rolex'],
                'search_type': 'specific'
            }

        return None

    def _check_category_patterns(self, query: str) -> Optional[Dict]:
        """Check for direct category mentions"""

        # Direct category match
        if match := self.patterns['category_direct'].search(query):
            category_word = match.group(1).lower()

            # Map to actual category
            category = self.category_map.get(category_word.rstrip('s'))
            if not category:
                category = self.category_map.get(category_word)

            if category:
                result = {
                    'category': category,
                    'tags': [category_word],
                    'search_type': 'general'
                }

                # Check for gender modifiers
                if 'men' in query and 'women' not in query:
                    if 'shoes' in category_word:
                        result['category'] = 'mens-shoes'
                    elif 'watch' in category_word:
                        result['category'] = 'mens-watches'
                    elif 'shirt' in category_word:
                        result['category'] = 'mens-shirts'
                    result['tags'].append('mens')

                elif 'women' in query or 'ladies' in query:
                    if 'shoes' in category_word:
                        result['category'] = 'womens-shoes'
                    elif 'watch' in category_word:
                        result['category'] = 'womens-watches'
                    elif 'dress' in category_word:
                        result['category'] = 'womens-dresses'
                    result['tags'].append('womens')

                # Extract price if mentioned
                if price_match := self._extract_price(query):
                    result.update(price_match)

                return result

        return None

    def _check_simple_patterns(self, query: str) -> Optional[Dict]:
        """Check for simple search patterns like 'show me X' or 'looking for X'"""

        # Try different patterns
        for pattern_name in ['show_me', 'looking_for', 'want']:
            if match := self.patterns[pattern_name].search(query):
                search_term = match.group(1).lower()

                # Look up in category map
                category = self.category_map.get(search_term)

                if category:
                    result = {
                        'category': category,
                        'title': search_term.title(),
                        'tags': [search_term],
                        'search_type': 'general'
                    }

                    # Extract price if mentioned
                    if price_match := self._extract_price(query):
                        result.update(price_match)

                    return result

        return None

    def _extract_price(self, query: str) -> Dict:
        """Extract price constraints from query"""
        result = {}

        # Under/below price
        if match := self.patterns['price_under'].search(query):
            result['price_max'] = float(match.group(1))
        elif match := self.patterns['price_below'].search(query):
            result['price_max'] = float(match.group(1))

        # Above price
        if match := self.patterns['price_above'].search(query):
            result['price_min'] = float(match.group(1))

        # Price range
        if match := self.patterns['price_range'].search(query):
            result['price_min'] = float(match.group(1))
            result['price_max'] = float(match.group(2))

        return result

# Initialize once at module level
fast_path_extractor = FastPathExtractor()
```

### 3.2 Fast Path Usage

```python
async def search_products_fast_path(query: str):
    """Try fast path first, fall back to LLM if needed"""

    # TIER 1: Pattern matching (0 LLM calls)
    quick_params = await fast_path_extractor.extract(query)

    if quick_params.matched and quick_params.confidence > 0.7:
        # Fast path succeeded! No LLM needed
        print(f"✅ Fast path: {query} -> {quick_params.confidence:.0%} confidence")
        return await execute_search(quick_params.__dict__)

    # TIER 2: Check cache before calling LLM
    cache_key = f"search_params:{hash(query)}"
    if cached_params := await cache.get(cache_key):
        print(f"✅ Cache hit: {query}")
        return await execute_search(cached_params)

    # TIER 3: LLM extraction (last resort)
    print(f"⚠️ LLM call: {query}")
    llm_params = await llm_extract_parameters(query)

    # Cache the result for 10 minutes
    await cache.set(cache_key, llm_params, ttl=600)

    return await execute_search(llm_params)
```

---

## 4. Database Optimization

### 4.1 Essential Indexes

```sql
-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating);
CREATE INDEX IF NOT EXISTS idx_products_availability ON products(availability_status);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_products_category_price
    ON products(category, price);

CREATE INDEX IF NOT EXISTS idx_products_category_brand
    ON products(category, brand);

-- Full-text search index (if using FTS)
CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
    title, description, tags, brand,
    content=products,
    tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS products_ai AFTER INSERT ON products BEGIN
    INSERT INTO products_fts(rowid, title, description, tags, brand)
    VALUES (new.id, new.title, new.description, new.tags, new.brand);
END;

CREATE TRIGGER IF NOT EXISTS products_ad AFTER DELETE ON products BEGIN
    DELETE FROM products_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS products_au AFTER UPDATE ON products BEGIN
    UPDATE products_fts
    SET title = new.title,
        description = new.description,
        tags = new.tags,
        brand = new.brand
    WHERE rowid = new.id;
END;
```

### 4.2 Optimized SQL Query with CTE

```python
async def execute_optimized_search(params: Dict) -> List[Product]:
    """
    Single optimized SQL query using Common Table Expression (CTE)
    for better performance
    """

    search_type = params.get('search_type', 'general')

    if search_type == 'specific':
        # Use FTS for specific product searches
        query = """
        WITH scored_products AS (
            SELECT
                p.*,
                -- Title scoring (highest weight)
                CASE
                    WHEN LOWER(p.title) = LOWER(?) THEN 100
                    WHEN LOWER(p.title) LIKE LOWER(?) || '%' THEN 80
                    WHEN LOWER(p.title) LIKE '%' || LOWER(?) || '%' THEN 60
                    ELSE 0
                END * 0.5 +
                -- Brand scoring
                CASE WHEN LOWER(p.brand) = LOWER(?) THEN 100 ELSE 0 END * 0.15 +
                -- Category scoring
                CASE WHEN p.category = ? THEN 100 ELSE 0 END * 0.2 +
                -- Tag scoring
                CASE
                    WHEN p.tags LIKE '%' || ? || '%' THEN 60
                    ELSE 0
                END * 0.15
                AS relevance_score
            FROM products p
            WHERE 1=1
                AND (? IS NULL OR LOWER(p.title) LIKE '%' || LOWER(?) || '%')
                AND (? IS NULL OR p.category = ?)
                AND (? IS NULL OR LOWER(p.brand) = LOWER(?))
                AND (? IS NULL OR p.price >= ?)
                AND (? IS NULL OR p.price <= ?)
        )
        SELECT * FROM scored_products
        WHERE relevance_score > 0
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 20
        """

        title = params.get('title', '')
        brand = params.get('brand')
        category = params.get('category')
        tags = params.get('tags', [])
        tag = tags[0] if tags else ''
        price_min = params.get('price_min')
        price_max = params.get('price_max')

        sql_params = (
            # Scoring params
            title, title, title,  # Title scoring
            brand or '',  # Brand scoring
            category or '',  # Category scoring
            tag,  # Tag scoring
            # Filter params
            title, title,  # Title filter
            category, category,  # Category filter
            brand, brand,  # Brand filter
            price_min, price_min,  # Price min filter
            price_max, price_max,  # Price max filter
        )

    else:  # general or hybrid search
        query = """
        WITH scored_products AS (
            SELECT
                p.*,
                -- Category scoring (highest for general)
                CASE WHEN p.category = ? THEN 100 ELSE 0 END * 0.4 +
                -- Tag scoring
                CASE
                    WHEN p.tags LIKE '%' || ? || '%' THEN 80
                    ELSE 0
                END * 0.3 +
                -- Title scoring
                CASE
                    WHEN LOWER(p.title) LIKE '%' || LOWER(?) || '%' THEN 60
                    ELSE 0
                END * 0.2 +
                -- Brand scoring
                CASE WHEN LOWER(p.brand) = LOWER(?) THEN 100 ELSE 0 END * 0.1
                AS relevance_score
            FROM products p
            WHERE 1=1
                AND (? IS NULL OR p.category = ?)
                AND (? IS NULL OR p.tags LIKE '%' || ? || '%')
                AND (? IS NULL OR LOWER(p.brand) = LOWER(?))
                AND (? IS NULL OR p.price >= ?)
                AND (? IS NULL OR p.price <= ?)
                AND p.availability_status = 'In Stock'
        )
        SELECT * FROM scored_products
        WHERE relevance_score > 0
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 50
        """

        category = params.get('category')
        tags = params.get('tags', [])
        tag = tags[0] if tags else ''
        title = params.get('title', '')
        brand = params.get('brand')
        price_min = params.get('price_min')
        price_max = params.get('price_max')

        sql_params = (
            # Scoring params
            category or '',  # Category scoring
            tag,  # Tag scoring
            title,  # Title scoring
            brand or '',  # Brand scoring
            # Filter params
            category, category,  # Category filter
            tag, tag,  # Tag filter
            brand, brand,  # Brand filter
            price_min, price_min,  # Price min filter
            price_max, price_max,  # Price max filter
        )

    results = await db_service.execute_query(query, sql_params)
    return [convert_row_to_product(row) for row in results]
```

---

## 5. Caching Strategy

### 5.1 Multi-Layer Cache

```python
from typing import Optional, Any
import hashlib
import json
from datetime import datetime, timedelta

class SearchCache:
    """Multi-layer caching for search results"""

    def __init__(self):
        # Layer 1: In-memory LRU cache (fastest)
        from functools import lru_cache
        self.memory_cache = {}
        self.cache_timestamps = {}
        self.max_memory_items = 1000

        # Layer 2: Redis cache (optional, for distributed systems)
        # self.redis_client = redis.Redis(...)

    def _generate_key(self, query: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from query and parameters"""
        cache_data = {
            'query': query.lower().strip(),
            'params': params or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    async def get(self, query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get from cache with TTL check"""
        key = self._generate_key(query, params)

        # Check memory cache first
        if key in self.memory_cache:
            timestamp = self.cache_timestamps.get(key)
            if timestamp and datetime.now() - timestamp < timedelta(minutes=10):
                return self.memory_cache[key]
            else:
                # Expired, remove
                del self.memory_cache[key]
                del self.cache_timestamps[key]

        # Check Redis cache (if available)
        # redis_result = await self.redis_client.get(key)
        # if redis_result:
        #     return json.loads(redis_result)

        return None

    async def set(self, query: str, value: Any, params: Optional[Dict] = None, ttl: int = 600):
        """Set cache with TTL"""
        key = self._generate_key(query, params)

        # Store in memory cache
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest item (simple FIFO)
            oldest_key = min(self.cache_timestamps, key=self.cache_timestamps.get)
            del self.memory_cache[oldest_key]
            del self.cache_timestamps[oldest_key]

        self.memory_cache[key] = value
        self.cache_timestamps[key] = datetime.now()

        # Store in Redis (if available)
        # await self.redis_client.setex(key, ttl, json.dumps(value))

    def invalidate_pattern(self, pattern: str):
        """Invalidate all cache entries matching pattern"""
        keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.memory_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]

    def clear(self):
        """Clear all cache"""
        self.memory_cache.clear()
        self.cache_timestamps.clear()

# Initialize cache singleton
search_cache = SearchCache()
```

### 5.2 Cache Usage in Search Flow

```python
async def search_with_caching(query: str, user_filters: Dict = None):
    """
    Complete search flow with caching at multiple levels
    """

    # Step 1: Check results cache (fastest)
    cache_key_results = f"results:{query}:{hash(str(user_filters))}"
    if cached_results := await search_cache.get(query, user_filters):
        return {
            'results': cached_results,
            'cache_hit': True,
            'source': 'cache',
            'timing_ms': 5  # Approximate
        }

    start_time = time.time()

    # Step 2: Fast path extraction (no LLM)
    quick_params = await fast_path_extractor.extract(query)

    if quick_params.matched and quick_params.confidence > 0.7:
        # Fast path success
        params = quick_params.__dict__
        extraction_method = 'fast_path'
        extraction_time = (time.time() - start_time) * 1000
    else:
        # Step 3: Check extraction cache before LLM
        cache_key_params = f"params:{query}"
        if cached_params := await search_cache.get(cache_key_params):
            params = cached_params
            extraction_method = 'cache'
            extraction_time = (time.time() - start_time) * 1000
        else:
            # Step 4: LLM extraction (last resort)
            params = await llm_extract_parameters(query)
            extraction_method = 'llm'
            extraction_time = (time.time() - start_time) * 1000

            # Cache extracted params for 10 minutes
            await search_cache.set(cache_key_params, params, ttl=600)

    # Step 5: Execute search
    search_start = time.time()
    results = await execute_optimized_search(params)
    search_time = (time.time() - search_start) * 1000

    # Step 6: Cache results for 5 minutes
    await search_cache.set(query, results, user_filters, ttl=300)

    total_time = (time.time() - start_time) * 1000

    return {
        'results': results,
        'cache_hit': False,
        'extraction_method': extraction_method,
        'timing': {
            'extraction_ms': extraction_time,
            'search_ms': search_time,
            'total_ms': total_time
        }
    }
```

---

## 6. TIER 2: Hybrid Path (NLP-Lite)

### 6.1 Using spaCy for Light NLP

```python
import spacy
from typing import Dict, List, Optional

class HybridExtractor:
    """
    Lightweight NLP extraction using spaCy.
    Faster than LLM, more sophisticated than regex.
    """

    def __init__(self):
        # Load small model for speed (en_core_web_sm is ~15MB)
        # Download: python -m spacy download en_core_web_sm
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.category_map = self._load_category_map()
        self.brand_entities = self._load_brand_entities()

    async def extract(self, query: str) -> Optional[Dict]:
        """
        Extract parameters using NLP techniques.
        Much faster than LLM (~20-50ms vs 500-2000ms)
        """
        doc = self.nlp(query.lower())

        result = {
            'category': None,
            'title': None,
            'brand': None,
            'tags': [],
            'search_type': 'general'
        }

        # Extract nouns (potential product names)
        nouns = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]

        # Extract brand (proper nouns or known brands)
        for token in doc:
            if token.pos_ == 'PROPN' and token.text.title() in self.brand_entities:
                result['brand'] = token.text.title()
                result['search_type'] = 'specific'

        # Extract category (check nouns against category map)
        for noun in nouns:
            if category := self.category_map.get(noun.lower()):
                result['category'] = category
                result['tags'].append(noun.lower())
                break

        # Extract product type (main noun phrase)
        if nouns:
            result['title'] = ' '.join(nouns).title()

        # Extract adjectives for tags
        adjectives = [token.text for token in doc if token.pos_ == 'ADJ']
        result['tags'].extend(adjectives)

        # Only return if we found something useful
        if result['category'] or result['brand'] or result['title']:
            return result

        return None

    def _load_category_map(self) -> Dict[str, str]:
        """Same as fast path"""
        # ... (reuse from FastPathExtractor)
        pass

    def _load_brand_entities(self) -> List[str]:
        """Same as fast path"""
        # ... (reuse from FastPathExtractor)
        pass

# Initialize
hybrid_extractor = HybridExtractor()
```

### 6.2 Complete Three-Tier Flow

```python
async def search_three_tier(query: str):
    """
    Complete three-tier search strategy:
    1. Fast Path (regex) - 60-70% of queries
    2. Hybrid Path (NLP) - 20-30% of queries
    3. LLM Path - 5-15% of queries
    """

    # TIER 1: Fast Path (Pattern Matching)
    quick_params = await fast_path_extractor.extract(query)
    if quick_params.matched and quick_params.confidence > 0.75:
        return await execute_optimized_search(quick_params.__dict__)

    # TIER 2: Hybrid Path (NLP-Lite)
    if hybrid_params := await hybrid_extractor.extract(query):
        return await execute_optimized_search(hybrid_params)

    # TIER 3: LLM Path (Full Extraction)
    # Check cache first
    cache_key = f"params:{query}"
    if cached_params := await search_cache.get(cache_key):
        return await execute_optimized_search(cached_params)

    # Last resort: Call LLM
    llm_params = await llm_extract_parameters(query)
    await search_cache.set(cache_key, llm_params, ttl=600)

    return await execute_optimized_search(llm_params)
```

---

## 7. Performance Monitoring

### 7.1 Metrics to Track

```python
from dataclasses import dataclass
from typing import Dict
import time

@dataclass
class SearchMetrics:
    """Track search performance metrics"""
    query: str
    extraction_method: str  # 'fast_path', 'hybrid', 'llm', 'cache'
    extraction_time_ms: float
    search_time_ms: float
    total_time_ms: float
    result_count: int
    cache_hit: bool
    timestamp: float

class MetricsCollector:
    """Collect and analyze search metrics"""

    def __init__(self):
        self.metrics: List[SearchMetrics] = []
        self.max_metrics = 10000  # Keep last 10k searches

    def record(self, metric: SearchMetrics):
        """Record a search metric"""
        self.metrics.append(metric)

        # Trim old metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]

    def get_stats(self, last_n: int = 1000) -> Dict:
        """Get performance statistics"""
        recent = self.metrics[-last_n:]

        if not recent:
            return {}

        # Calculate stats
        total_searches = len(recent)
        fast_path = sum(1 for m in recent if m.extraction_method == 'fast_path')
        hybrid_path = sum(1 for m in recent if m.extraction_method == 'hybrid')
        llm_path = sum(1 for m in recent if m.extraction_method == 'llm')
        cache_hits = sum(1 for m in recent if m.cache_hit)

        avg_total_time = sum(m.total_time_ms for m in recent) / total_searches
        avg_extraction_time = sum(m.extraction_time_ms for m in recent) / total_searches
        avg_search_time = sum(m.search_time_ms for m in recent) / total_searches

        return {
            'total_searches': total_searches,
            'distribution': {
                'fast_path_pct': (fast_path / total_searches) * 100,
                'hybrid_path_pct': (hybrid_path / total_searches) * 100,
                'llm_path_pct': (llm_path / total_searches) * 100,
                'cache_hit_pct': (cache_hits / total_searches) * 100,
            },
            'avg_timing_ms': {
                'extraction': avg_extraction_time,
                'search': avg_search_time,
                'total': avg_total_time,
            },
            'llm_call_reduction': ((total_searches - llm_path) / total_searches) * 100,
        }

# Initialize metrics collector
metrics_collector = MetricsCollector()
```

### 7.2 Instrumented Search Function

```python
async def search_with_metrics(query: str, user_filters: Dict = None):
    """Search with full metrics tracking"""

    start_time = time.time()
    extraction_start = time.time()

    # Try three-tier extraction
    extraction_method = None
    params = None

    # Tier 1: Fast path
    quick_params = await fast_path_extractor.extract(query)
    if quick_params.matched and quick_params.confidence > 0.75:
        params = quick_params.__dict__
        extraction_method = 'fast_path'

    # Tier 2: Hybrid
    elif hybrid_params := await hybrid_extractor.extract(query):
        params = hybrid_params
        extraction_method = 'hybrid'

    # Tier 3: Check cache
    elif cached_params := await search_cache.get(f"params:{query}"):
        params = cached_params
        extraction_method = 'cache'

    # Tier 4: LLM (last resort)
    else:
        params = await llm_extract_parameters(query)
        extraction_method = 'llm'
        await search_cache.set(f"params:{query}", params, ttl=600)

    extraction_time = (time.time() - extraction_start) * 1000

    # Execute search
    search_start = time.time()
    results = await execute_optimized_search(params)
    search_time = (time.time() - search_start) * 1000

    total_time = (time.time() - start_time) * 1000

    # Record metrics
    metric = SearchMetrics(
        query=query,
        extraction_method=extraction_method,
        extraction_time_ms=extraction_time,
        search_time_ms=search_time,
        total_time_ms=total_time,
        result_count=len(results),
        cache_hit=extraction_method == 'cache',
        timestamp=time.time()
    )
    metrics_collector.record(metric)

    return {
        'results': results,
        'metrics': {
            'extraction_method': extraction_method,
            'timing_ms': {
                'extraction': extraction_time,
                'search': search_time,
                'total': total_time
            }
        }
    }
```

---

## 8. Implementation Roadmap

### Phase 1: Quick Wins (Week 1)

- ✅ Implement Fast Path extractor with regex patterns
- ✅ Add database indexes
- ✅ Optimize SQL query (use CTE)
- ✅ Add in-memory caching

**Expected Gains:** 50-60% LLM reduction, 3-5x faster

### Phase 2: Advanced Optimization (Week 2)

- ✅ Implement Hybrid Path with spaCy
- ✅ Add multi-layer caching
- ✅ Implement metrics tracking
- ✅ Query optimization and testing

**Expected Gains:** 70-80% LLM reduction, 5-8x faster

### Phase 3: Scale & Polish (Week 3)

- ✅ Add Redis caching (optional)
- ✅ Implement SQLite FTS5
- ✅ Connection pooling
- ✅ Load testing and optimization

**Expected Gains:** 85%+ LLM reduction, 10x faster

### Phase 4: Advanced Features (Future)

- Vector embeddings for semantic search
- Personalized results
- A/B testing framework
- Real-time analytics dashboard

---

## 9. Expected Performance After Optimization

### 9.1 Query Distribution (Target)

| Tier | Method            | % of Queries | Avg Response Time | LLM Calls |
| ---- | ----------------- | ------------ | ----------------- | --------- |
| 1    | Fast Path (Regex) | 60-70%       | 10-30ms           | 0         |
| 2    | Hybrid (NLP)      | 20-25%       | 30-80ms           | 0         |
| 3    | Cache Hit         | 5-10%        | 5-15ms            | 0         |
| 4    | LLM               | 5-10%        | 500-2000ms        | 1         |

**Overall Average:** 50-100ms (down from 800ms)
**LLM Usage:** 5-10% (down from 100%)

### 9.2 Cost Savings

**Before Optimization:**

- 10,000 queries/day × $0.005/query = $50/day = $1,500/month

**After Optimization:**

- 10,000 queries/day × 10% × $0.005/query = $5/day = $150/month

**Savings:** $1,350/month (90% reduction)

---

## 10. Testing Strategy

### 10.1 Performance Tests

```python
import asyncio
import time
from typing import List

async def benchmark_search_methods():
    """Benchmark different search methods"""

    test_queries = [
        # Fast path queries
        "iPhone 14",
        "MacBook Pro",
        "Nike Air Jordan",
        "show me laptops",
        "looking for smartphones",

        # Hybrid queries
        "comfortable running shoes",
        "affordable gaming laptop",
        "elegant women's watch",

        # Complex queries (LLM needed)
        "I need a gift for my tech-savvy friend who loves Apple products",
        "Something stylish for a business professional under $200",
    ]

    results = {
        'fast_path': [],
        'hybrid': [],
        'llm': [],
    }

    for query in test_queries:
        # Test fast path
        start = time.time()
        fast_result = await fast_path_extractor.extract(query)
        fast_time = (time.time() - start) * 1000

        if fast_result.matched:
            results['fast_path'].append(fast_time)
            print(f"✅ Fast: {query} -> {fast_time:.1f}ms")
            continue

        # Test hybrid
        start = time.time()
        hybrid_result = await hybrid_extractor.extract(query)
        hybrid_time = (time.time() - start) * 1000

        if hybrid_result:
            results['hybrid'].append(hybrid_time)
            print(f"🔸 Hybrid: {query} -> {hybrid_time:.1f}ms")
            continue

        # Test LLM
        start = time.time()
        llm_result = await llm_extract_parameters(query)
        llm_time = (time.time() - start) * 1000
        results['llm'].append(llm_time)
        print(f"⚠️ LLM: {query} -> {llm_time:.1f}ms")

    # Print summary
    print("\n=== Performance Summary ===")
    for method, times in results.items():
        if times:
            avg_time = sum(times) / len(times)
            print(f"{method}: {len(times)} queries, avg {avg_time:.1f}ms")

# Run benchmark
asyncio.run(benchmark_search_methods())
```

---

## 11. Summary

### Key Optimizations

1. **Three-Tier Extraction**

   - Fast Path (regex): 60-70% of queries, 10-30ms
   - Hybrid Path (NLP): 20-25% of queries, 30-80ms
   - LLM Path: 5-10% of queries, 500-2000ms

2. **Multi-Layer Caching**

   - Results cache: 5-15ms response
   - Params cache: Avoid duplicate LLM calls
   - Smart TTL management

3. **Database Optimization**

   - Strategic indexes
   - Single optimized CTE query
   - FTS5 for full-text search

4. **Performance Gains**
   - **8-10x faster** average response time
   - **85-90% reduction** in LLM calls
   - **90% cost savings** on API usage

### Implementation Priority

**Must Have (Week 1):**

- ✅ Fast Path extractor
- ✅ Database indexes
- ✅ Optimized SQL query
- ✅ Basic caching

**Should Have (Week 2):**

- ✅ Hybrid Path (NLP)
- ✅ Metrics tracking
- ✅ Multi-layer caching

**Nice to Have (Week 3+):**

- Redis caching
- FTS5 integration
- Advanced analytics

---

**Document Version:** 2.0 (Optimized)  
**Date:** October 5, 2025  
**Focus:** Performance & Cost Optimization  
**Target:** <100ms response, 85%+ LLM reduction
