# Product Search Pipeline - Technical Implementation Guide

**Version:** 1.0 - Technical Deep Dive  
**Date:** October 5, 2025  
**Purpose:** Detailed implementation guide with code examples

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Database Schema & Indexes](#2-database-schema--indexes)
3. [Type Definitions](#3-type-definitions)
4. [LLM Parameter Extraction](#4-llm-parameter-extraction)
5. [Search Query Engine](#5-search-query-engine)
6. [Scoring Algorithm Implementation](#6-scoring-algorithm-implementation)
7. [Filtering & Post-Processing](#7-filtering--post-processing)
8. [Fallback Strategies](#8-fallback-strategies)
9. [Integration Guide](#9-integration-guide)
10. [Testing & Validation](#10-testing--validation)

---

## 1. Architecture Overview

### 1.1 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND                                                         │
│ User Input: "I want iPhone 14 under $1000"                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ API LAYER: /api/product-search                                  │
│ File: app/api/routes/product_search.py                          │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LANGGRAPH WORKFLOW                                              │
│ File: app/graph/workflows/product_search/graph.py               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Node 1: extract_search_parameters                        │  │
│  │ File: nodes/extract_search_parameters.py                 │  │
│  │ - Calls LLM with structured output                       │  │
│  │ - Returns: Entities object                               │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │ Node 2: execute_product_query                            │  │
│  │ File: nodes/execute_product_query.py                     │  │
│  │ - Builds SQL query from parameters                       │  │
│  │ - Calls ProductService                                   │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────▼─────────────────────────────────────┐  │
│  │ Node 3: format_results                                   │  │
│  │ File: nodes/format_results.py                            │  │
│  │ - Formats products for frontend                          │  │
│  │ - Adds metadata                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE LAYER                                                  │
│ Service: app/services/db/product.py (ProductService)            │
│ Database: SQLite (app_database.sqlite)                          │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 File Structure

```
app/
├── graph/
│   └── workflows/
│       └── product_search/
│           ├── graph.py                    # LangGraph workflow definition
│           ├── types.py                    # TypedDict definitions
│           └── nodes/
│               ├── extract_search_parameters.py
│               ├── execute_product_query.py
│               └── format_results.py
├── services/
│   └── db/
│       └── product.py                      # Database queries
├── models/
│   └── classifier.py                       # Entities model (Pydantic)
└── api/
    └── routes/
        └── product_search.py               # API endpoint
```

---

## 2. Database Schema & Indexes

### 2.1 Products Table Schema

```sql
-- Full products table schema
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    discount_percentage REAL DEFAULT 0,
    rating REAL DEFAULT 0,
    stock INTEGER DEFAULT 0,
    tags TEXT,                              -- JSON array as string
    brand TEXT,
    sku TEXT UNIQUE,
    weight REAL,
    dimensions TEXT,                        -- JSON object as string
    warranty_information TEXT,
    shipping_information TEXT,
    availability_status TEXT DEFAULT 'In Stock',
    return_policy TEXT,
    minimum_order_quantity INTEGER DEFAULT 1,
    thumbnail TEXT,
    images TEXT,                            -- JSON array as string
    barcode TEXT,
    qr_code TEXT,
    available_sizes TEXT,                   -- JSON array as string
    unit TEXT DEFAULT 'piece',
    gender TEXT DEFAULT 'U',                -- M, F, U
    material TEXT,
    style TEXT,
    pattern TEXT,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Essential Indexes for Performance

```sql
-- Primary search indexes (MUST HAVE)
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products(category);

CREATE INDEX IF NOT EXISTS idx_products_brand
    ON products(brand);

CREATE INDEX IF NOT EXISTS idx_products_price
    ON products(price);

CREATE INDEX IF NOT EXISTS idx_products_rating
    ON products(rating DESC);

CREATE INDEX IF NOT EXISTS idx_products_stock
    ON products(stock DESC);

CREATE INDEX IF NOT EXISTS idx_products_availability
    ON products(availability_status);

CREATE INDEX IF NOT EXISTS idx_products_gender
    ON products(gender);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_category_price
    ON products(category, price);

CREATE INDEX IF NOT EXISTS idx_products_category_brand
    ON products(category, brand);

CREATE INDEX IF NOT EXISTS idx_products_category_rating
    ON products(category, rating DESC);

CREATE INDEX IF NOT EXISTS idx_products_brand_price
    ON products(brand, price);

-- Full-text search index (OPTIONAL - for Phase 2)
CREATE INDEX IF NOT EXISTS idx_products_title_lower
    ON products(LOWER(title));
```

### 2.3 Database Statistics

```sql
-- Analyze tables for query optimization
ANALYZE products;

-- View index usage (for debugging)
SELECT * FROM sqlite_stat1 WHERE tbl = 'products';
```

---

## 3. Type Definitions

### 3.1 Core Types (app/graph/workflows/product_search/types.py)

```python
from typing import Any, Dict, List, TypedDict, Optional
from app.types.common import CommonState, AuthState


class Product(TypedDict):
    """Product data structure matching database schema"""
    id: int
    title: str
    description: str
    category: str
    price: float
    discount_percentage: float
    rating: float
    stock: int
    tags: List[str]                         # Parsed from JSON string
    brand: str
    sku: str
    weight: float
    dimensions: Dict[str, float]            # Parsed from JSON string
    warranty_information: str
    shipping_information: str
    availability_status: str
    return_policy: str
    minimum_order_quantity: int
    thumbnail: str
    images: List[str]                       # Parsed from JSON string
    barcode: str
    qr_code: str
    available_sizes: List[str]              # Parsed from JSON string
    unit: str
    gender: str
    material: Optional[str]
    style: Optional[str]
    pattern: Optional[str]
    color: Optional[str]


class SearchParameters(TypedDict):
    """Extracted search parameters from LLM"""
    search_type: Optional[str]              # 'specific', 'general', 'hybrid'
    product_category: Optional[str]         # e.g., 'smartphones', 'laptops'
    title: Optional[str]                    # e.g., 'iPhone 14', 'Laptop'
    tags: Optional[List[str]]               # e.g., ['electronics', 'apple']
    brand: Optional[str]                    # e.g., 'Apple', 'Nike'
    price_min: Optional[float]
    price_max: Optional[float]
    rating_min: Optional[float]
    gender: Optional[str]                   # 'male', 'female', 'unisex'
    availability_status: Optional[str]       # 'In Stock', 'Low Stock'
    color: Optional[str]
    material: Optional[str]
    style: Optional[str]


class ProductSearchState(CommonState, AuthState):
    """LangGraph state for product search workflow"""
    search_query: str                       # Original user query
    search_parameters: SearchParameters     # Extracted parameters
    search_results: List[Product]           # Query results
    result_count: int                       # Number of results
    suggestions: List[Dict[str, Any]]       # Fallback suggestions

    # Inherited from CommonState:
    # - thread_id: str
    # - conversation_history: List[Dict]
    # - user_message: str
    # - ai_message: str

    # Inherited from AuthState:
    # - user_id: Optional[int]
    # - session_token: Optional[str]
    # - is_authenticated: bool
```

### 3.2 Pydantic Models (app/models/classifier.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional


class Entities(BaseModel):
    """
    Pydantic model for structured LLM output.
    Used with .with_structured_output() for parameter extraction.
    """

    # Search classification
    search_type: Optional[str] = Field(
        default="general",
        description="Type of search: 'specific', 'general', or 'hybrid'"
    )

    # Primary search fields
    product_category: Optional[str] = Field(
        default=None,
        description="Product category (e.g., 'smartphones', 'laptops')"
    )

    title: Optional[str] = Field(
        default=None,
        description="Product name or type for title matching"
    )

    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="List of tags for broader search"
    )

    # Brand and attributes
    brand: Optional[str] = Field(
        default=None,
        description="Brand name (e.g., 'Apple', 'Nike')"
    )

    # Filters
    price_min: Optional[float] = Field(
        default=None,
        description="Minimum price",
        ge=0
    )

    price_max: Optional[float] = Field(
        default=None,
        description="Maximum price",
        ge=0
    )

    rating_min: Optional[float] = Field(
        default=None,
        description="Minimum rating (0-5)",
        ge=0,
        le=5
    )

    gender: Optional[str] = Field(
        default=None,
        description="Target gender: 'male', 'female', or 'unisex'"
    )

    availability_status: Optional[str] = Field(
        default=None,
        description="Stock status: 'In Stock', 'Low Stock', 'Out of Stock'"
    )

    # Optional attributes
    color: Optional[str] = Field(default=None)
    material: Optional[str] = Field(default=None)
    style: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "search_type": "specific",
                "product_category": "smartphones",
                "title": "iPhone 14",
                "tags": ["electronics", "apple", "smartphone"],
                "brand": "Apple",
                "price_max": 1000,
                "rating_min": 4.0
            }
        }
```

---

## 4. LLM Parameter Extraction

### 4.1 Implementation (nodes/extract_search_parameters.py)

```python
from typing import cast
from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.models.classifier import Entities
from app.services.llm import llm_service
from app.utils.conversation_context import format_conversation_context_with_template


async def extract_search_parameters_node(state: ProductSearchState) -> ProductSearchState:
    """
    LangGraph node for extracting search parameters from user query.

    Flow:
    1. Get user message from state
    2. Format conversation context
    3. Build LLM prompt with instructions
    4. Call LLM with structured output (Pydantic model)
    5. Update state with extracted parameters

    Args:
        state: Current workflow state

    Returns:
        Updated state with search_parameters populated
    """

    # Step 1: Get user message
    user_message = state.get("search_query", "")
    if not user_message:
        user_message = state.get("user_message", "")

    # Step 2: Format conversation context
    # This includes previous messages for context-aware extraction
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="parameter_extraction",
        limit=5,  # Include last 5 messages
        fallback_message=""
    )

    # Step 3: Build extraction prompt
    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", get_extraction_system_prompt()),
        ("user", "{query}"),
        ("user", "{conversation_context}")
    ])

    # Step 4: Call LLM with structured output
    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    messages = extractor_prompt.invoke({
        "query": user_message,
        "conversation_context": conversation_context
    })

    # Use structured output to get Pydantic model
    response: Entities = cast(
        Entities,
        await llm.with_structured_output(Entities).ainvoke(messages)
    )

    # Step 5: Update state
    entities_dict = response.model_dump()

    state["search_query"] = user_message
    state["search_parameters"] = entities_dict
    state["search_results"] = []
    state["suggestions"] = []
    state["result_count"] = 0

    return state


def get_extraction_system_prompt() -> str:
    """
    Detailed system prompt for parameter extraction.
    This is the core of the extraction logic.
    """
    return """
You are a parameter extractor for an e-commerce product search system.
Your task is to extract structured parameters from natural language queries.

---

## SEARCH TYPE CLASSIFICATION

First, determine the search type:

1. **SPECIFIC SEARCH**
   - User mentions a specific product name, model, or unique identifier
   - Examples: "iPhone 14", "MacBook Pro 16 inch", "Nike Air Jordan 1"
   - Set search_type = "specific"
   - Prioritize exact title matching

2. **GENERAL SEARCH**
   - User asks for a category or product type without specifics
   - Examples: "smartphones", "laptops", "running shoes", "beauty products"
   - Set search_type = "general"
   - Focus on category and tag matching

3. **HYBRID SEARCH**
   - Combination of category and specific attributes
   - Examples: "Apple laptops", "Nike running shoes under $100", "red dresses"
   - Set search_type = "hybrid"
   - Match category + brand/attributes

---

## FIELD EXTRACTION RULES

### 1. CATEGORY (product_category)

Extract the main product category. Use EXACT category names from this list:

```

beauty, fragrances, furniture, groceries, home-decoration,
smartphones, laptops, tablets, mens-shirts, mens-shoes, mens-watches,
womens-dresses, womens-shoes, womens-watches, womens-bags, womens-jewellery,
sunglasses, automotive, motorcycle, lighting, sports-accessories,
kitchen-accessories, mobile-accessories, skincare, tops, vehicle

````

**Mapping examples:**
- "phone", "mobile" → smartphones
- "laptop", "computer", "notebook" → laptops
- "tablet", "ipad" → tablets
- "makeup", "cosmetics" → beauty
- "perfume", "cologne" → fragrances
- "food", "snacks" → groceries
- "shoes" → mens-shoes (unless specified otherwise)
- "watch" → mens-watches (unless specified otherwise)

**Gender handling:**
- If "men's" or "for men" → use mens-* category
- If "women's" or "ladies" → use womens-* category
- If unspecified → default to mens-* or womens-* based on context

### 2. TITLE

Extract the main product name for title matching.

**For specific searches:**
- Extract exact product name: "iPhone 14 Pro", "MacBook Pro 16 inch"
- Include important details: color, size, model
- Capitalize properly: "iPhone 14" not "iphone 14"

**For general searches:**
- Extract product type: "Laptop", "Dress", "Shoes"
- Include descriptive words if mentioned: "Gaming Laptop", "Red Dress"

**Examples:**
- "I want an iPhone 14" → title: "iPhone 14"
- "Show me red dresses" → title: "Red Dress"
- "Looking for gaming laptops" → title: "Gaming Laptop"
- "Need running shoes" → title: "Running Shoes"

### 3. TAGS

Generate 2-5 searchable tags for broader matching.

**Rules:**
- Use lowercase
- Include main product type
- Add synonyms and related terms
- Include category-related terms
- Be general enough to match various products

**Examples:**
- "iPhone 14" → ["smartphones", "apple", "electronics", "mobile"]
- "gaming laptop" → ["laptops", "gaming", "computers", "electronics"]
- "red dress" → ["dresses", "clothing", "fashion", "womens"]
- "running shoes" → ["shoes", "footwear", "athletic", "running", "sports"]

### 4. BRAND

Extract brand name when explicitly mentioned.

**Examples:**
- "Apple iPhone" → brand: "Apple"
- "Nike shoes" → brand: "Nike"
- "Samsung Galaxy" → brand: "Samsung"
- "Rolex watch" → brand: "Rolex"

Capitalize properly: "Apple" not "apple"

### 5. PRICE FILTERS

Extract price constraints from natural language.

**Patterns:**
- "under $500", "below $500" → price_max: 500
- "above $100", "over $100" → price_min: 100
- "between $50 and $200" → price_min: 50, price_max: 200
- "around $300" → price_min: 250, price_max: 350

### 6. RATING

Extract rating requirements.

**Patterns:**
- "4+ stars", "highly rated" → rating_min: 4.0
- "5 stars", "top rated" → rating_min: 4.5
- "good reviews" → rating_min: 3.5

### 7. GENDER

Determine target gender.

**Rules:**
- "men's", "for men" → gender: "male"
- "women's", "ladies" → gender: "female"
- Unspecified → gender: "unisex"

### 8. AVAILABILITY

Extract stock status if mentioned.

**Patterns:**
- "in stock", "available now" → availability_status: "In Stock"
- "low stock" → availability_status: "Low Stock"

---

## OUTPUT FORMAT

Return a JSON object with extracted parameters. Set fields to null if not mentioned.

Example:
```json
{
    "search_type": "specific",
    "product_category": "smartphones",
    "title": "iPhone 14",
    "tags": ["smartphones", "apple", "electronics", "mobile"],
    "brand": "Apple",
    "price_min": null,
    "price_max": 1000,
    "rating_min": 4.0,
    "gender": "unisex",
    "availability_status": null,
    "color": null,
    "material": null,
    "style": null
}
````

---

## IMPORTANT NOTES

1. **DO NOT** include explanations in the output
2. **DO NOT** make assumptions - if not mentioned, set to null
3. **BE PRECISE** with category names - use exact matches
4. **PRIORITIZE** title and tags for search effectiveness
5. **CONSIDER CONTEXT** from conversation history
   """

````

### 4.2 Conversation Context Integration

```python
# app/utils/conversation_context.py

from typing import Dict, List, Any


def format_conversation_context_with_template(
    state: Dict[str, Any],
    template_name: str,
    limit: int = 5,
    fallback_message: str = ""
) -> str:
    """
    Format conversation history for context-aware extraction.

    Args:
        state: Current workflow state
        template_name: Template identifier (e.g., "parameter_extraction")
        limit: Maximum number of previous messages to include
        fallback_message: Message if no history exists

    Returns:
        Formatted conversation context string
    """
    conversation_history = state.get("conversation_history", [])

    if not conversation_history:
        return fallback_message

    # Get last N messages
    recent_history = conversation_history[-limit:]

    # Format for parameter extraction
    if template_name == "parameter_extraction":
        context_parts = ["Previous conversation context:"]

        for msg in recent_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "user":
                context_parts.append(f"User: {content}")
            elif role == "assistant":
                context_parts.append(f"Assistant: {content}")

        return "\n".join(context_parts)

    return fallback_message
````

---

## 5. Search Query Engine

### 5.1 ProductService Implementation

```python
# app/services/db/product.py

import json
from typing import Any, Dict, List, Optional, cast
from app.services.db.db import Product, db_service


class ProductService:
    """
    Service for product database operations.
    Handles query building, execution, and result parsing.
    """

    def __init__(self):
        self.db_service = db_service

    def _convert_row_to_product(self, row: tuple) -> Product:
        """
        Convert database row tuple to Product TypedDict.

        Database returns tuples in column order. We need to parse
        JSON strings and construct the Product object.

        Args:
            row: Database row tuple

        Returns:
            Product TypedDict
        """
        # Parse JSON fields
        tags = json.loads(row[8]) if row[8] else []
        dimensions = json.loads(row[12]) if row[12] else {}
        images = json.loads(row[19]) if row[19] else []
        available_sizes = json.loads(row[22]) if row[22] else []

        return cast(Product, {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "category": row[3],
            "price": row[4],
            "discount_percentage": row[5],
            "rating": row[6],
            "stock": row[7],
            "tags": json.dumps(tags),  # Re-serialize for consistency
            "brand": row[9],
            "sku": row[10],
            "weight": row[11],
            "dimensions": json.dumps(dimensions),
            "warranty_information": row[13],
            "shipping_information": row[14],
            "availability_status": row[15],
            "return_policy": row[16],
            "minimum_order_quantity": row[17],
            "thumbnail": row[18],
            "images": json.dumps(images),
            "barcode": row[20],
            "qr_code": row[21],
            "available_sizes": json.dumps(available_sizes),
            "unit": row[23],
            "gender": row[24],
        })

    async def get_products(
        self,
        product_details: Dict[str, Any]
    ) -> List[Product]:
        """
        Main search method - builds and executes product query.

        Args:
            product_details: Extracted search parameters

        Returns:
            List of matching products
        """
        # Build query dynamically based on parameters
        conditions = []
        params = []

        # 1. Category filter (exact match)
        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])

        # 2. Gender filter (exact match or unisex)
        if product_details.get("gender"):
            gender_code = product_details["gender"][0].upper()  # M, F, U
            conditions.append("(gender = ? OR gender = 'U')")
            params.append(gender_code)

        # 3. Price range filters
        if product_details.get("price_min"):
            conditions.append("price >= ?")
            params.append(product_details["price_min"])

        if product_details.get("price_max"):
            conditions.append("price <= ?")
            params.append(product_details["price_max"])

        # 4. Rating filter
        if product_details.get("rating_min"):
            conditions.append("rating >= ?")
            params.append(product_details["rating_min"])

        # 5. Brand filter (case-insensitive partial match)
        if product_details.get("brand"):
            conditions.append("LOWER(brand) LIKE LOWER(?)")
            params.append(f"%{product_details['brand']}%")

        # 6. Availability filter
        if product_details.get("availability_status"):
            conditions.append("availability_status = ?")
            params.append(product_details["availability_status"])

        # 7. Title and tag search (primary search mechanism)
        search_conditions = []

        # Title search - case insensitive
        if product_details.get("title"):
            title = product_details["title"].lower()
            search_conditions.append("LOWER(title) LIKE ?")
            params.append(f"%{title}%")

        # Tag-based search - search in tags, title, and description
        if product_details.get("tags"):
            tags = product_details["tags"]

            for tag in tags:
                tag_lower = tag.lower()
                # Search across multiple fields for each tag
                search_conditions.append(
                    "(LOWER(tags) LIKE ? OR LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
                )
                params.extend([f"%{tag_lower}%", f"%{tag_lower}%", f"%{tag_lower}%"])

        # Combine search conditions with OR
        if search_conditions:
            conditions.append("(" + " OR ".join(search_conditions) + ")")

        # Build final query
        query = "SELECT * FROM products"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add ordering (by rating and stock)
        query += " ORDER BY rating DESC, stock DESC"

        # Limit results
        query += " LIMIT 50"

        # Execute query
        params_tuple = tuple(params) if params else None
        results = await db_service.execute_query(query, params_tuple)

        # Convert results to Product objects
        products = cast(List[Product], [])
        if results:
            for row in results:
                products.append(self._convert_row_to_product(row))

        return products

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get single product by ID"""
        query = "SELECT * FROM products WHERE id = ? LIMIT 1"
        results = await db_service.execute_query(query, (product_id,))

        if results:
            return self._convert_row_to_product(results[0])

        return None

    async def search_products(
        self,
        search_term: str,
        limit: int = 20
    ) -> List[Product]:
        """
        Simple text search across title, description, brand, and tags.
        Used for quick searches or fallback.
        """
        query = """
        SELECT * FROM products
        WHERE LOWER(title) LIKE LOWER(?)
           OR LOWER(description) LIKE LOWER(?)
           OR LOWER(brand) LIKE LOWER(?)
           OR LOWER(tags) LIKE LOWER(?)
        ORDER BY rating DESC, stock DESC
        LIMIT ?
        """

        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern, limit)

        results = await db_service.execute_query(query, params)

        products = cast(List[Product], [])
        if results:
            for row in results:
                products.append(self._convert_row_to_product(row))

        return products


# Initialize service singleton
product_service = ProductService()
```

### 5.2 Query Execution Node

```python
# nodes/execute_product_query.py

from app.graph.workflows.product_search.types import ProductSearchState
from app.services.db.product import product_service


async def execute_product_query_node(state: ProductSearchState) -> ProductSearchState:
    """
    Execute product search query using extracted parameters.

    Flow:
    1. Get search parameters from state
    2. Call ProductService with parameters
    3. Update state with results

    Args:
        state: Current workflow state with search_parameters

    Returns:
        Updated state with search_results and result_count
    """

    # Get search parameters
    search_params = state.get("search_parameters", {})

    # Execute search
    products = await product_service.get_products(search_params)

    # Update state
    state["search_results"] = products
    state["result_count"] = len(products)

    return state
```

---

## 6. Scoring Algorithm Implementation

### 6.1 Enhanced ProductService with Scoring

```python
# Enhanced version with relevance scoring

async def get_products_with_scoring(
    self,
    product_details: Dict[str, Any]
) -> List[Product]:
    """
    Search with relevance scoring for better result ranking.

    Scoring weights:
    - Title match: 50%
    - Category match: 15%
    - Tag match: 20%
    - Brand match: 5%
    - Description match: 10%
    """

    search_type = product_details.get("search_type", "general")

    if search_type == "specific":
        # For specific searches, prioritize exact title matches
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
                WHEN LOWER(tags) LIKE '%' || LOWER(?) || '%' THEN 60
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
            {additional_filters}
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 20
        """

        title = product_details.get("title", "")
        category = product_details.get("product_category", "")
        tags = product_details.get("tags", [])
        tag = tags[0] if tags else ""
        brand = product_details.get("brand", "")

        # Build additional filters
        filter_conditions = []
        filter_params = []

        if product_details.get("price_min"):
            filter_conditions.append("price >= ?")
            filter_params.append(product_details["price_min"])

        if product_details.get("price_max"):
            filter_conditions.append("price <= ?")
            filter_params.append(product_details["price_max"])

        additional_filters = ""
        if filter_conditions:
            additional_filters = "AND " + " AND ".join(filter_conditions)

        query = query.format(additional_filters=additional_filters)

        # Combine all params
        params = (
            title, title, title,  # Title scoring params
            category,             # Category scoring
            tag,                  # Tag scoring
            brand,                # Brand scoring
            title,                # Description scoring
            *filter_params        # Additional filters
        )

    else:  # general or hybrid search
        # For general searches, prioritize category and tags
        query = """
        SELECT *,
            (CASE
                WHEN category = ? THEN 100
                ELSE 0
            END) * 0.4 +
            (CASE
                WHEN LOWER(tags) LIKE '%' || LOWER(?) || '%' THEN 80
                ELSE 0
            END) * 0.3 +
            (CASE
                WHEN LOWER(title) LIKE '%' || LOWER(?) || '%' THEN 60
                ELSE 0
            END) * 0.2 +
            (CASE
                WHEN LOWER(brand) = LOWER(?) THEN 100
                ELSE 0
            END) * 0.1
        AS relevance_score
        FROM products
        WHERE relevance_score > 0
            {additional_filters}
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 50
        """

        category = product_details.get("product_category", "")
        tags = product_details.get("tags", [])
        tag = tags[0] if tags else ""
        title = product_details.get("title", "")
        brand = product_details.get("brand", "")

        # Build additional filters (same as above)
        filter_conditions = []
        filter_params = []

        if product_details.get("price_min"):
            filter_conditions.append("price >= ?")
            filter_params.append(product_details["price_min"])

        if product_details.get("price_max"):
            filter_conditions.append("price <= ?")
            filter_params.append(product_details["price_max"])

        additional_filters = ""
        if filter_conditions:
            additional_filters = "AND " + " AND ".join(filter_conditions)

        query = query.format(additional_filters=additional_filters)

        params = (
            category,       # Category scoring
            tag,            # Tag scoring
            title,          # Title scoring
            brand,          # Brand scoring
            *filter_params  # Additional filters
        )

    # Execute query
    results = await db_service.execute_query(query, params)

    # Convert and return products
    products = cast(List[Product], [])
    if results:
        for row in results:
            # Note: relevance_score will be the last column
            product = self._convert_row_to_product(row[:-1])  # Exclude score column
            products.append(product)

    return products
```

---

## 7. Filtering & Post-Processing

### 7.1 Result Filtering

```python
# nodes/filter_results.py

from typing import List, Dict, Any
from app.graph.workflows.product_search.types import ProductSearchState, Product


async def filter_results_node(state: ProductSearchState) -> ProductSearchState:
    """
    Apply post-query filtering and ranking adjustments.

    This node runs after the initial query to:
    1. Apply complex filters not done in SQL
    2. Adjust rankings based on business rules
    3. Remove duplicates
    4. Apply personalization (future)
    """

    products = state.get("search_results", [])
    search_params = state.get("search_parameters", {})

    # 1. Apply color filter if specified
    if color := search_params.get("color"):
        products = [p for p in products if p.get("color") == color]

    # 2. Apply material filter if specified
    if material := search_params.get("material"):
        products = [p for p in products if p.get("material") == material]

    # 3. Apply style filter if specified
    if style := search_params.get("style"):
        products = [p for p in products if p.get("style") == style]

    # 4. Remove out-of-stock items (unless explicitly requested)
    if not search_params.get("include_out_of_stock"):
        products = [p for p in products if p["stock"] > 0]

    # 5. Apply business rules
    products = apply_business_rules(products, search_params)

    # 6. Remove duplicates (by SKU)
    seen_skus = set()
    unique_products = []
    for product in products:
        sku = product.get("sku")
        if sku not in seen_skus:
            seen_skus.add(sku)
            unique_products.append(product)

    # Update state
    state["search_results"] = unique_products
    state["result_count"] = len(unique_products)

    return state


def apply_business_rules(
    products: List[Product],
    search_params: Dict[str, Any]
) -> List[Product]:
    """
    Apply business rules to product results.

    Rules:
    1. Boost products with high ratings
    2. Boost products with good availability
    3. Boost new products (if we track that)
    4. De-prioritize low stock items
    """

    for product in products:
        boost = 0

        # Rule 1: High rating boost
        if product["rating"] >= 4.5:
            boost += 10
        elif product["rating"] >= 4.0:
            boost += 5

        # Rule 2: Good availability boost
        if product["stock"] > 100:
            boost += 5

        # Rule 3: Low stock penalty
        if product["stock"] < 10:
            boost -= 5

        # Apply boost (we'll store this temporarily)
        product["_boost_score"] = boost

    # Sort by boost score (higher is better)
    products.sort(key=lambda p: p.get("_boost_score", 0), reverse=True)

    # Remove temporary boost score
    for product in products:
        product.pop("_boost_score", None)

    return products
```

---

## 8. Fallback Strategies

### 8.1 Fallback Node Implementation

```python
# nodes/handle_fallback.py

from typing import List, Dict, Any
from app.graph.workflows.product_search.types import ProductSearchState
from app.services.db.product import product_service


async def handle_fallback_node(state: ProductSearchState) -> ProductSearchState:
    """
    Handle cases where search returns no or few results.

    Fallback strategies:
    1. No results (0) → Relax filters and suggest alternatives
    2. Few results (1-2) → Suggest related products
    3. Good results (3+) → Pass through unchanged
    """

    result_count = state.get("result_count", 0)
    search_params = state.get("search_parameters", {})

    # Strategy 1: Good results - no fallback needed
    if result_count >= 3:
        return state

    # Strategy 2: No results - aggressive fallback
    if result_count == 0:
        return await handle_zero_results(state, search_params)

    # Strategy 3: Few results - gentle expansion
    if result_count < 3:
        return await handle_few_results(state, search_params)

    return state


async def handle_zero_results(
    state: ProductSearchState,
    search_params: Dict[str, Any]
) -> ProductSearchState:
    """
    Handle zero results by relaxing constraints.

    Steps:
    1. Remove price constraints
    2. Search by category only
    3. Generate suggestions
    """

    suggestions = []

    # Try 1: Remove price constraints
    relaxed_params = search_params.copy()
    relaxed_params.pop("price_min", None)
    relaxed_params.pop("price_max", None)

    products = await product_service.get_products(relaxed_params)

    if products:
        state["search_results"] = products[:10]
        state["result_count"] = len(products)
        suggestions.append({
            "type": "relaxed_price",
            "message": "No products found in your price range. Showing all available options.",
            "action": "remove_price_filter"
        })
    else:
        # Try 2: Category only
        if category := search_params.get("product_category"):
            category_products = await product_service.get_products({
                "product_category": category
            })

            if category_products:
                state["search_results"] = category_products[:10]
                state["result_count"] = len(category_products)
                suggestions.append({
                    "type": "category_only",
                    "message": f"No exact matches found. Showing all {category} products.",
                    "action": "browse_category"
                })
            else:
                # Try 3: Popular products
                popular_products = await product_service.get_products({})
                state["search_results"] = popular_products[:10]
                state["result_count"] = len(popular_products)
                suggestions.append({
                    "type": "popular",
                    "message": "No matches found. Here are our popular products.",
                    "action": "browse_popular"
                })

    # Generate "Did you mean?" suggestions
    if brand := search_params.get("brand"):
        similar_brands = await find_similar_brands(brand)
        if similar_brands:
            suggestions.append({
                "type": "brand_suggestion",
                "message": "Did you mean?",
                "options": similar_brands
            })

    state["suggestions"] = suggestions

    return state


async def handle_few_results(
    state: ProductSearchState,
    search_params: Dict[str, Any]
) -> ProductSearchState:
    """
    Expand search slightly to include more results.
    """

    current_products = state.get("search_results", [])

    # Try related products from same category
    if category := search_params.get("product_category"):
        related_products = await product_service.get_products({
            "product_category": category
        })

        # Add products not already in results
        current_ids = {p["id"] for p in current_products}
        new_products = [
            p for p in related_products
            if p["id"] not in current_ids
        ]

        # Add up to 5 related products
        state["search_results"] = current_products + new_products[:5]
        state["result_count"] = len(state["search_results"])

        if new_products:
            state["suggestions"] = [{
                "type": "related",
                "message": "We also found these related products you might like."
            }]

    return state


async def find_similar_brands(brand: str) -> List[str]:
    """
    Find brands similar to the given brand name.
    Uses simple string similarity (Levenshtein distance).
    """
    # Get all unique brands from database
    query = "SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL"
    results = await db_service.execute_query(query)

    all_brands = [row[0] for row in results if row[0]]

    # Simple similarity check (can be enhanced with fuzzy matching)
    similar = []
    brand_lower = brand.lower()

    for db_brand in all_brands:
        db_brand_lower = db_brand.lower()

        # Check if similar (contains, or edit distance < 2)
        if (brand_lower in db_brand_lower or
            db_brand_lower in brand_lower or
            levenshtein_distance(brand_lower, db_brand_lower) <= 2):
            similar.append(db_brand)

    return similar[:5]  # Return top 5


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
```

---

## 9. Integration Guide

### 9.1 LangGraph Workflow Definition

```python
# app/graph/workflows/product_search/graph.py

from langgraph.graph import StateGraph, END
from app.graph.workflows.product_search.types import ProductSearchState
from app.graph.workflows.product_search.nodes.extract_search_parameters import extract_search_parameters_node
from app.graph.workflows.product_search.nodes.execute_product_query import execute_product_query_node
from app.graph.workflows.product_search.nodes.filter_results import filter_results_node
from app.graph.workflows.product_search.nodes.handle_fallback import handle_fallback_node
from app.graph.workflows.product_search.nodes.format_results import format_results_node


def create_product_search_workflow() -> StateGraph:
    """
    Create the product search LangGraph workflow.

    Flow:
    1. Extract parameters from user query (LLM)
    2. Execute database query
    3. Filter results
    4. Handle fallback if needed
    5. Format results for output
    """

    # Create workflow
    workflow = StateGraph(ProductSearchState)

    # Add nodes
    workflow.add_node("extract_parameters", extract_search_parameters_node)
    workflow.add_node("execute_query", execute_product_query_node)
    workflow.add_node("filter_results", filter_results_node)
    workflow.add_node("handle_fallback", handle_fallback_node)
    workflow.add_node("format_results", format_results_node)

    # Define edges (workflow flow)
    workflow.set_entry_point("extract_parameters")
    workflow.add_edge("extract_parameters", "execute_query")
    workflow.add_edge("execute_query", "filter_results")
    workflow.add_edge("filter_results", "handle_fallback")
    workflow.add_edge("handle_fallback", "format_results")
    workflow.add_edge("format_results", END)

    return workflow.compile()


# Initialize workflow
product_search_workflow = create_product_search_workflow()
```

### 9.2 API Endpoint

````python
# app/api/routes/product_search.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.graph.workflows.product_search.graph import product_search_workflow


router = APIRouter(prefix="/product-search", tags=["Product Search"])


class SearchRequest(BaseModel):
    """Request model for product search"""
    query: str
    user_id: Optional[int] = None
    thread_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response model for product search"""
    products: List[Dict[str, Any]]
    result_count: int
    suggestions: List[Dict[str, Any]]
    thread_id: str


@router.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """
    Product search endpoint.

    Example request:
    ```json
    {
        "query": "iPhone 14 under $1000",
        "user_id": 123,
        "thread_id": "thread_abc123"
    }
    ```

    Example response:
    ```json
    {
        "products": [...],
        "result_count": 5,
        "suggestions": [],
        "thread_id": "thread_abc123"
    }
    ```
    """

    try:
        # Prepare initial state
        initial_state = {
            "search_query": request.query,
            "user_id": request.user_id,
            "thread_id": request.thread_id or generate_thread_id(),
            "conversation_history": [],
            "search_parameters": {},
            "search_results": [],
            "result_count": 0,
            "suggestions": []
        }

        # Apply additional filters if provided
        if request.filters:
            initial_state["search_parameters"].update(request.filters)

        # Execute workflow
        result = await product_search_workflow.ainvoke(initial_state)

        # Format response
        return SearchResponse(
            products=result["search_results"],
            result_count=result["result_count"],
            suggestions=result.get("suggestions", []),
            thread_id=result["thread_id"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def generate_thread_id() -> str:
    """Generate unique thread ID for conversation tracking"""
    import uuid
    return f"thread_{uuid.uuid4().hex[:12]}"
````

---

## 10. Testing & Validation

### 10.1 Unit Tests

```python
# tests/test_product_search.py

import pytest
from app.services.db.product import product_service
from app.graph.workflows.product_search.nodes.extract_search_parameters import extract_search_parameters_node


@pytest.mark.asyncio
async def test_extract_parameters_specific_search():
    """Test parameter extraction for specific product search"""

    state = {
        "search_query": "I want an iPhone 14 under $1000",
        "conversation_history": []
    }

    result = await extract_search_parameters_node(state)

    params = result["search_parameters"]
    assert params["search_type"] == "specific"
    assert params["title"] == "iPhone 14"
    assert params["product_category"] == "smartphones"
    assert params["brand"] == "Apple"
    assert params["price_max"] == 1000


@pytest.mark.asyncio
async def test_extract_parameters_general_search():
    """Test parameter extraction for general category search"""

    state = {
        "search_query": "Show me laptops",
        "conversation_history": []
    }

    result = await extract_search_parameters_node(state)

    params = result["search_parameters"]
    assert params["search_type"] == "general"
    assert params["product_category"] == "laptops"


@pytest.mark.asyncio
async def test_product_search_with_filters():
    """Test product search with price and rating filters"""

    search_params = {
        "product_category": "smartphones",
        "price_max": 1000,
        "rating_min": 4.0
    }

    products = await product_service.get_products(search_params)

    assert len(products) > 0
    for product in products:
        assert product["category"] == "smartphones"
        assert product["price"] <= 1000
        assert product["rating"] >= 4.0


@pytest.mark.asyncio
async def test_search_no_results_fallback():
    """Test fallback behavior when no results found"""

    search_params = {
        "product_category": "nonexistent-category",
        "brand": "NonexistentBrand"
    }

    products = await product_service.get_products(search_params)

    # Should return empty list
    assert len(products) == 0
```

### 10.2 Integration Tests

```python
# tests/test_product_search_integration.py

import pytest
from app.graph.workflows.product_search.graph import product_search_workflow


@pytest.mark.asyncio
async def test_full_workflow_specific_search():
    """Test complete workflow for specific product search"""

    initial_state = {
        "search_query": "MacBook Pro 16 inch",
        "thread_id": "test_thread_1",
        "conversation_history": [],
        "user_id": None
    }

    result = await product_search_workflow.ainvoke(initial_state)

    # Verify results
    assert result["result_count"] > 0
    assert "search_parameters" in result
    assert "search_results" in result

    # Check parameters
    params = result["search_parameters"]
    assert params["search_type"] == "specific"
    assert "macbook" in params["title"].lower()

    # Check products
    products = result["search_results"]
    assert all("title" in p for p in products)
    assert all("price" in p for p in products)


@pytest.mark.asyncio
async def test_full_workflow_with_price_filter():
    """Test workflow with price constraints"""

    initial_state = {
        "search_query": "gaming laptops under $1500",
        "thread_id": "test_thread_2",
        "conversation_history": []
    }

    result = await product_search_workflow.ainvoke(initial_state)

    # Verify price filter applied
    products = result["search_results"]
    assert all(p["price"] <= 1500 for p in products)


@pytest.mark.asyncio
async def test_workflow_zero_results_fallback():
    """Test fallback when no results found"""

    initial_state = {
        "search_query": "unicorn laptops under $1",
        "thread_id": "test_thread_3",
        "conversation_history": []
    }

    result = await product_search_workflow.ainvoke(initial_state)

    # Should have suggestions even with no direct results
    assert "suggestions" in result
    assert len(result["suggestions"]) > 0
```

### 10.3 Performance Tests

```python
# tests/test_product_search_performance.py

import pytest
import time
from app.graph.workflows.product_search.graph import product_search_workflow


@pytest.mark.asyncio
async def test_search_performance():
    """Test that search completes within acceptable time"""

    test_queries = [
        "iPhone 14",
        "laptops under $2000",
        "Nike running shoes",
        "beauty products",
        "Samsung Galaxy"
    ]

    times = []

    for query in test_queries:
        initial_state = {
            "search_query": query,
            "thread_id": f"perf_test_{query[:10]}",
            "conversation_history": []
        }

        start = time.time()
        result = await product_search_workflow.ainvoke(initial_state)
        elapsed = time.time() - start

        times.append(elapsed)

        # Each search should complete in < 3 seconds
        assert elapsed < 3.0, f"Search too slow: {elapsed:.2f}s for '{query}'"

    avg_time = sum(times) / len(times)
    print(f"\nAverage search time: {avg_time:.2f}s")
    print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")
```

---

## 11. Deployment Checklist

### 11.1 Pre-Deployment

```bash
# 1. Create database indexes
python -c "from app.services.db.db import db_service; import asyncio; asyncio.run(db_service.create_indexes())"

# 2. Run tests
pytest tests/test_product_search.py -v

# 3. Run integration tests
pytest tests/test_product_search_integration.py -v

# 4. Check database performance
sqlite3 app_database.sqlite "EXPLAIN QUERY PLAN SELECT * FROM products WHERE category = 'laptops' LIMIT 10;"

# 5. Verify LLM configuration
python -c "from app.services.llm import llm_service; print(llm_service.get_llm_without_tools())"
```

### 11.2 Monitoring

```python
# Add logging to track performance

import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)


def log_execution_time(func):
    """Decorator to log function execution time"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000

        logger.info(f"{func.__name__} took {elapsed:.2f}ms")
        return result

    return wrapper


# Apply to key functions
@log_execution_time
async def extract_search_parameters_node(state):
    ...

@log_execution_time
async def execute_product_query_node(state):
    ...
```

---

## 12. Summary

### Implementation Steps

1. ✅ Set up database schema and indexes
2. ✅ Define TypedDict and Pydantic models
3. ✅ Implement LLM parameter extraction
4. ✅ Build ProductService with query logic
5. ✅ Create LangGraph workflow nodes
6. ✅ Add filtering and fallback logic
7. ✅ Create API endpoint
8. ✅ Write comprehensive tests
9. ✅ Deploy and monitor

### Key Files Modified/Created

```
app/
├── graph/workflows/product_search/
│   ├── graph.py (workflow definition)
│   ├── types.py (TypedDicts)
│   └── nodes/
│       ├── extract_search_parameters.py
│       ├── execute_product_query.py
│       ├── filter_results.py
│       ├── handle_fallback.py
│       └── format_results.py
├── services/db/
│   └── product.py (enhanced)
├── models/
│   └── classifier.py (Entities model)
└── api/routes/
    └── product_search.py (API endpoint)
```

### Performance Targets

- Parameter extraction: < 500-1000ms (LLM call)
- Database query: < 50ms (with indexes)
- Total response time: < 1500ms
- Results: Top 20-50 products, ranked by relevance

---

**Document Version:** 1.0 (Technical Implementation)  
**Date:** October 5, 2025  
**Status:** Ready for Implementation
