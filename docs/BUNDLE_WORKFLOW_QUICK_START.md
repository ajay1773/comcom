# Bundle Recommendation Workflow - Quick Start Guide

## 🎯 What It Does

Recommends **multiple related products** when users ask about activities or use cases.

**Example**:

- User: "I want to play cricket, what equipment do I need?"
- System: Returns cricket bat, ball, pads, gloves, helmet, shoes (all grouped and prioritized)

---

## 🏗️ Architecture at a Glance

```
User Query
    ↓
Classifier (detects "product_bundle_search" intent)
    ↓
Orchestrator (routes to bundle workflow)
    ↓
┌─────────────────────────────────────────┐
│   Product Bundle Search Workflow        │
│                                          │
│  1️⃣ Identify Bundle Items (LLM)         │
│     - Analyzes use case                 │
│     - Lists all needed products         │
│     - Assigns priorities (1-3)          │
│     - Generates search keywords         │
│                                          │
│  2️⃣ Execute Bundle Search               │
│     - Searches for each item            │
│     - Uses existing product_service     │
│     - Respects priority limits          │
│                                          │
│  3️⃣ Format Bundle Results               │
│     - Groups by priority                │
│     - Creates widget JSON               │
│     - Generates text summary            │
└─────────────────────────────────────────┘
    ↓
Output Handler
    ↓
Frontend Display (grouped cards)
```

---

## 📋 Implementation Checklist

### Backend (Python)

- [ ] **Step 1**: Add enums (`app/core/enums.py`)

  ```python
  WorkflowType.PRODUCT_BUNDLE_SEARCH
  NodeName.PRODUCT_BUNDLE_SEARCH_WORKFLOW
  ```

- [ ] **Step 2**: Update classifier (`app/models/classifier.py`)

  ```python
  intent: Literal["product_bundle_search", ...]
  ```

- [ ] **Step 3**: Create workflow directory

  ```
  app/graph/workflows/product_bundle_search/
    ├── __init__.py
    ├── types.py
    ├── graph.py
    └── nodes/
        ├── __init__.py
        ├── identify_bundle_items.py
        ├── execute_bundle_search.py
        ├── format_bundle_results.py
        └── runner.py
  ```

- [ ] **Step 4**: Implement LLM bundle identification

  - Create `BundleAnalysis` Pydantic model
  - Write LLM prompt for use case analysis
  - Extract bundle items with priorities

- [ ] **Step 5**: Implement search logic

  - Loop through bundle items
  - Call `product_service.search_products_fts()` for each
  - Group results by category

- [ ] **Step 6**: Create graph and runner

  - Define 3-node graph
  - Create runner function
  - Handle state transformations

- [ ] **Step 7**: Register in base graph

  - Add node to base graph
  - Add routing edge
  - Update orchestrator mapping

- [ ] **Step 8**: Update classifier prompt
  - Add bundle search examples
  - Differentiate from product_search

### Frontend (TypeScript/React)

- [ ] **Step 9**: Create bundle display component

  ```
  client/src/features/product-bundle-search/
    └── views/
        └── bundle-results/
            └── index.tsx
  ```

- [ ] **Step 10**: Implement grouped display

  - Essential items section (red badge)
  - Recommended items section (blue badge)
  - Optional items section (gray badge)
  - Product cards with add-to-cart

- [ ] **Step 11**: Register template
  - Add to `signed-out-chat-window.tsx`
  - Map "product_bundle_results" to component

---

## 🔑 Key Code Snippets

### 1. LLM Bundle Identification

```python
class BundleAnalysis(BaseModel):
    bundle_title: str
    bundle_description: str
    items: List[BundleItemSchema]
    user_level_detected: str

async def identify_bundle_items_node(state):
    prompt = """Analyze use case and identify ALL products needed.
    Prioritize: 1=essential, 2=recommended, 3=optional"""

    chain = prompt | llm.with_structured_output(BundleAnalysis)
    result = await chain.ainvoke({"use_case": state["use_case"]})

    return {"bundle_items": result.items, ...}
```

### 2. Product Search Loop

```python
async def execute_bundle_search_node(state):
    bundle_results = {}

    for item in state["bundle_items"]:
        search_params = {"keywords": item["keywords"]}
        products = await product_service.search_products_fts(search_params)
        bundle_results[item["category"]] = products

    return {"bundle_results": bundle_results}
```

### 3. Widget JSON Format

```json
{
  "template": "product_bundle_results",
  "payload": {
    "bundle_title": "Cricket Starter Kit",
    "bundle_description": "Everything you need to start playing cricket",
    "essential_items": {
      "cricket bat": [product1, product2, ...],
      "cricket ball": [product3, product4, ...]
    },
    "recommended_items": {...},
    "optional_items": {...}
  }
}
```

---

## 🧪 Test Cases

### Test 1: Cricket Equipment

**Query**: "I want to play cricket, what do I need?"

**Expected Bundle Items**:

- Priority 1: Cricket bat, cricket ball, batting pads
- Priority 2: Cricket gloves, helmet, cricket shoes
- Priority 3: Kitbag, water bottle

### Test 2: Camping Trip

**Query**: "I'm going camping next week, what should I buy?"

**Expected Bundle Items**:

- Priority 1: Tent, sleeping bag, flashlight
- Priority 2: Camping stove, backpack, first aid kit
- Priority 3: Portable charger, camping chair

### Test 3: Home Gym

**Query**: "I want to start working out at home"

**Expected Bundle Items**:

- Priority 1: Yoga mat, dumbbells, resistance bands
- Priority 2: Jump rope, foam roller, exercise ball
- Priority 3: Kettlebell, pull-up bar, ankle weights

---

## 🎨 Frontend Display Layout

```
┌──────────────────────────────────────────────────┐
│  Cricket Starter Kit                              │
│  Everything you need to start playing cricket     │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  🔴 Essential Items                               │
│  ┌──────────────────────────────────────────┐    │
│  │  Cricket Bat                              │    │
│  │  For batting and scoring runs             │    │
│  │  ┌───────┐ ┌───────┐ ┌───────┐          │    │
│  │  │Product│ │Product│ │Product│           │    │
│  │  │  $50  │ │  $75  │ │ $100  │           │    │
│  │  └───────┘ └───────┘ └───────┘          │    │
│  └──────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────┐    │
│  │  Cricket Ball                             │    │
│  │  For bowling and fielding                 │    │
│  │  ┌───────┐ ┌───────┐                     │    │
│  │  │Product│ │Product│                      │    │
│  │  │  $10  │ │  $15  │                      │    │
│  │  └───────┘ └───────┘                     │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  🔵 Recommended Items                             │
│  (Similar layout...)                              │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  ⚫ Optional Upgrades                             │
│  (Similar layout...)                              │
└──────────────────────────────────────────────────┘
```

---

## ⚡ Quick Implementation Steps

### Phase 1: Core Backend (2-3 hours)

1. Add enums and update classifier
2. Create types.py with state definitions
3. Create identify_bundle_items.py with LLM logic

### Phase 2: Search Logic (1-2 hours)

4. Create execute_bundle_search.py
5. Create format_bundle_results.py

### Phase 3: Integration (1-2 hours)

6. Create graph.py and runner.py
7. Register in base.py
8. Update orchestrator mapping

### Phase 4: Frontend (3-4 hours)

9. Create BundleResults component
10. Register template in chat window
11. Style with Tailwind

### Phase 5: Testing (2 hours)

12. Test with cricket, camping, gym queries
13. Verify grouping and display
14. Test add-to-cart from bundle

---

## 📊 Success Criteria

✅ **LLM Accuracy**: Identifies 90%+ relevant products for use case  
✅ **Coverage**: All essential items included in bundle  
✅ **Grouping**: Proper priority assignment (essential/recommended/optional)  
✅ **Display**: Clear, organized UI with grouped cards  
✅ **Integration**: Seamless add-to-cart from bundle  
✅ **Performance**: Response time < 5 seconds

---

## 🚀 Ready to Implement!

Start with Phase 1 and work through sequentially. Each phase builds on the previous one. The LLM-powered bundle identification is the core intelligence that makes this work.

**Total Implementation Time**: ~13-19 hours for full feature

---

## 💡 Pro Tips

1. **Reuse Existing Code**: The `product_service.search_products_fts()` already exists - just call it multiple times
2. **LLM is Key**: Spend time on the prompt engineering for bundle identification
3. **Prioritization Matters**: Use priority to show more/fewer options per item
4. **Test Iteratively**: Test each node independently before connecting the graph
5. **Start Simple**: Implement basic bundle first, add features like budget optimization later

---

Need help with any specific part? The detailed implementation plan has complete code for all nodes!
