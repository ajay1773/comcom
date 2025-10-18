# Product Bundle Search Workflow Overview

## What It Does

The Product Bundle Search workflow helps users discover complete product sets for specific activities, hobbies, or use cases. Instead of searching for individual items, users can request bundles like "I want to play cricket" or "I'm going camping" and receive a curated collection of all necessary products organized by priority.

---

## Workflow Architecture

### Entry Point

**Trigger**: When classifier detects `product_bundle_search` intent  
**Example Queries**:

- "I want to play cricket, what equipment do I need?"
- "Show me everything for camping"
- "I need gear for starting a home gym"

### Flow Diagram

```
User Query → Classifier → Bundle Search Workflow
                              ↓
                    1. Identify Bundle Items (LLM)
                              ↓
                    2. Execute Bundle Search (DB)
                              ↓
                    3. Format Results (LLM)
                              ↓
                    Output: Text Response + Widget JSON
```

---

## Node-by-Node Breakdown

### 1. **Identify Bundle Items Node** (`identify_bundle_items.py`)

**Purpose**: Uses LLM to analyze user's activity and identify all needed products

**Input**:

- User's query/use case
- Optional: user level (beginner/intermediate/professional)
- Optional: budget

**LLM Task**:

- Understand the activity (e.g., "cricket", "camping", "photography")
- Break down into specific product categories
- Assign priorities: 1=Essential, 2=Recommended, 3=Optional
- Generate search keywords for each item
- Suggest quantities
- Create bundle title and description

**Output Example**:

```python
{
    "bundle_title": "Cricket Starter Kit",
    "bundle_description": "Everything you need to start playing cricket",
    "bundle_items": [
        {
            "category": "cricket bat",
            "purpose": "batting",
            "keywords": "cricket bat",
            "priority": 1,  # Essential
            "quantity": 1
        },
        {
            "category": "cricket ball",
            "purpose": "bowling and practice",
            "keywords": "cricket ball leather",
            "priority": 1,  # Essential
            "quantity": 2
        },
        {
            "category": "cricket gloves",
            "purpose": "hand protection",
            "keywords": "cricket batting gloves",
            "priority": 2,  # Recommended
            "quantity": 1
        },
        {
            "category": "cricket shoes",
            "purpose": "specialized footwear",
            "keywords": "cricket shoes spikes",
            "priority": 3,  # Optional
            "quantity": 1
        }
    ]
}
```

**Key Intelligence**:

- Detects user level automatically
- Adjusts recommendations based on expertise
- Considers safety items (helmets, pads)
- Understands domain-specific needs

---

### 2. **Execute Bundle Search Node** (`execute_bundle_search.py`)

**Purpose**: Search for actual products for each identified bundle item

**Process**:

1. Loop through each bundle item
2. Extract search keywords and priority
3. Call `product_service.search_products_fts()` for each item
4. Limit results based on priority:
   - Priority 1 (Essential): Top 5 products
   - Priority 2 (Recommended): Top 3 products
   - Priority 3 (Optional): Top 2 products
5. Store products grouped by category

**Search Parameters**:

```python
{
    "keywords": item["keywords"],
    "in_stock_only": True,
    "sort_by": "relevance"
}
```

**Output**:

```python
{
    "bundle_results": {
        "cricket bat": [
            {
                "id": 1,
                "title": "Professional Cricket Bat",
                "brand": "Nike",
                "price": 89.99,
                "rating": 4.5,
                "thumbnail": "...",
                "priority": 1,
                "purpose": "batting",
                "quantity": 1
            },
            # ... 4 more products
        ],
        "cricket ball": [...],
        "cricket gloves": [...]
    },
    "result_count": 23
}
```

**Features**:

- Reuses existing FTS5 search infrastructure
- Filters in-stock items only
- Maintains priority information with products
- Handles missing products gracefully

---

### 3. **Format Bundle Results Node** (`format_bundle_results.py`)

**Purpose**: Format results and generate natural language response using LLM

**Two Scenarios**:

#### A. No Results Found

- **LLM generates** a friendly apology message
- Suggests trying different activities
- Returns `null` widget JSON

**Example Response**:

> "I'd love to help you with cricket equipment! Unfortunately, we don't have those items available right now. Feel free to ask about other activities or check back soon!"

#### B. Products Found

1. **Group products by priority**:

   - Essential items (priority 1)
   - Recommended items (priority 2)
   - Optional upgrades (priority 3)

2. **Create widget JSON** for frontend:

```json
{
    "template": "product_bundle_results",
    "payload": {
        "bundle_title": "Cricket Starter Kit",
        "bundle_description": "Everything you need to start playing cricket",
        "essential_items": { "cricket bat": [...], "cricket ball": [...] },
        "recommended_items": { "cricket gloves": [...] },
        "optional_items": { "cricket shoes": [...] },
        "total_categories": 4,
        "total_products": 23
    }
}
```

3. **LLM generates** conversational response:
   - Acknowledges the request enthusiastically
   - Mentions the curated bundle
   - Explains priority organization
   - Encourages exploration

**Example Response**:

> "I've put together a great cricket starter kit for you! I've organized everything into must-haves, recommended items, and optional upgrades to make it easy to find what you need. Take a look at the products below and let me know if you'd like to add anything to your cart!"

**Output**:

```python
{
    "workflow_output_text": "<LLM-generated friendly message>",
    "workflow_output_json": { widget_json }
}
```

---

## State Management

### ProductBundleSearchState

```python
{
    # Input
    "search_query": "I want to play cricket",
    "use_case": "play cricket",
    "user_level": "beginner",
    "budget_total": None,

    # After Node 1
    "bundle_items": [...],
    "bundle_title": "Cricket Starter Kit",
    "bundle_description": "...",

    # After Node 2
    "bundle_results": {...},
    "result_count": 23,

    # After Node 3
    "workflow_output_text": "<LLM response>",
    "workflow_output_json": {...}
}
```

### Runner Integration

The `run_product_bundle_search()` function:

1. Extracts or initializes sub-state from global state
2. Updates with current user message and auth context
3. Invokes the workflow subgraph
4. Merges updated sub-state back to global state
5. Output handler extracts final response

---

## Frontend Display

### Component: `BundleResults`

**Location**: `client/src/features/product-bundle-search/views/bundle-results/index.tsx`

**Features**:

- Displays bundle title and description
- Groups products by priority with color coding:
  - 🔴 Essential (red border)
  - 🔵 Recommended (blue border)
  - ⚫ Optional (gray border)
- Shows product cards with image, title, brand, price
- "Add to Cart" button for each product
- Responsive grid layout

---

## Key Differentiators

### vs. Product Search

| Feature      | Product Search       | Bundle Search                                 |
| ------------ | -------------------- | --------------------------------------------- |
| Input        | Specific product     | Activity/use case                             |
| Output       | Single product list  | Grouped by category + priority                |
| Intelligence | Parameter extraction | Complete need analysis                        |
| Organization | Flat list            | Hierarchical (essential/recommended/optional) |

### Advantages

1. **Complete Solution**: User gets everything needed, not just one item
2. **Priority Guidance**: Helps users decide what's essential vs. nice-to-have
3. **Beginner Friendly**: Perfect for users new to an activity
4. **Time Saving**: No need to search for each item individually
5. **Discovery**: Users learn about items they might not have considered

---

## Example User Journey

### Query: "I want to play cricket"

1. **Classifier**: Detects `product_bundle_search` intent

2. **Node 1 - LLM Analysis**:

   - Identifies needed items: bat, ball, pads, gloves, helmet, shoes
   - Assigns priorities based on necessity
   - Creates "Cricket Starter Kit" bundle

3. **Node 2 - Product Search**:

   - Searches for each category
   - Finds 5 bats, 4 balls, 3 pads, etc.
   - Total: 23 products across 6 categories

4. **Node 3 - Format & Response**:

   - Groups products by priority
   - LLM generates: "I've put together a cricket starter kit..."
   - Creates widget JSON with organized products

5. **Frontend Display**:
   - Shows friendly message
   - Displays bundle in organized sections
   - User can add individual items to cart

---

## Technical Highlights

### LLM Integration

- **2 LLM Calls**:
  1. Bundle item identification (structured output)
  2. Natural language response generation (conversational)
- Uses `llm_service.get_llm()` and `llm_service.get_llm_without_tools()`

### Database Integration

- Leverages existing `product_service.search_products_fts()`
- FTS5 full-text search for fast, accurate results
- Filters by stock availability

### State Architecture

- Sub-state pattern isolates workflow data
- Integrates with global state for auth and conversation history
- Type-safe with TypedDict definitions

---

## Future Enhancements

### Potential Additions

1. **Budget Optimization**: Filter products by total budget
2. **Smart Substitutions**: Suggest alternatives for out-of-stock items
3. **Bundle Discounts**: "Save 15% when buying complete bundle"
4. **User Level Detection**: Adjust recommendations for beginner/expert
5. **Comparison Mode**: Budget vs. Premium bundle options
6. **Bundle Templates**: Pre-defined popular bundles
7. **Quantity Optimization**: Suggest optimal quantities based on activity duration

---

## Summary

The Product Bundle Search workflow transforms user activity requests into complete product recommendations using:

- **LLM intelligence** to understand needs and generate responses
- **Existing search infrastructure** for reliable product retrieval
- **Priority-based organization** for better user decision-making
- **Natural language responses** for conversational experience

It bridges the gap between "I want to do X" and "Here's everything you need for X", making it easier for users to get started with new activities without domain expertise.
