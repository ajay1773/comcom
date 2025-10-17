# Bundle/Equipment Recommendation Workflow - Implementation Plan

## Overview

This document provides a comprehensive implementation plan for a **Bundle Recommendation Workflow** that intelligently suggests multiple related products based on a user's activity or use case.

### Example Use Cases

- **Cricket Equipment**: "I want to play cricket" → bat, ball, pads, gloves, helmet
- **Camping Gear**: "I'm going camping" → tent, sleeping bag, flashlight, backpack
- **Home Gym**: "I want to start working out at home" → dumbbells, yoga mat, resistance bands
- **Gaming Setup**: "I want to setup a gaming station" → gaming mouse, keyboard, headset, monitor

---

## Architecture Overview

### Workflow Type: `product_bundle_search`

This workflow extends the existing product search infrastructure but focuses on **multi-product recommendations** based on **use case analysis** rather than single product search.

### Key Differences from Product Search

| Feature        | Product Search      | Bundle Search                            |
| -------------- | ------------------- | ---------------------------------------- |
| **Query Type** | Specific product    | Activity/Use case                        |
| **Results**    | Single product type | Multiple product types                   |
| **Grouping**   | None                | Grouped by category/function             |
| **LLM Role**   | Extract filters     | Identify related items + Extract filters |
| **UI Display** | Product grid        | Grouped cards/sections                   |

---

## Implementation Plan

### Phase 1: Backend Infrastructure

#### 1.1 Add Workflow Type & Node Name

**File**: `app/core/enums.py`

```python
class WorkflowType(str, Enum):
    # ... existing types ...
    PRODUCT_BUNDLE_SEARCH = "product_bundle_search"

class NodeName(str, Enum):
    # ... existing nodes ...
    PRODUCT_BUNDLE_SEARCH_WORKFLOW = "product_bundle_search_workflow"
```

#### 1.2 Update Classifier Model

**File**: `app/models/classifier.py`

Update the `intent` field to include the new bundle search intent:

```python
class Classifier(BaseModel):
    intent: Literal[
        "product_search",
        "product_bundle_search",  # NEW
        "place_order",
        # ... rest of intents ...
    ]
```

#### 1.3 Create Bundle Search State

**File**: `app/graph/workflows/product_bundle_search/types.py` (NEW)

```python
from typing import TypedDict, List, Dict, Any, Optional
from app.types.common import CommonState

class BundleItem(TypedDict):
    """Represents a single item in the bundle"""
    category: str  # e.g., "cricket bat", "cricket ball"
    purpose: str  # e.g., "batting", "bowling"
    keywords: str  # search keywords for this item
    priority: int  # 1 (essential), 2 (recommended), 3 (optional)
    quantity: int  # suggested quantity

class ProductBundleSearchState(CommonState):
    """State for product bundle search workflow"""

    # Input from user
    use_case: str  # "play cricket", "camping trip", "home gym"
    user_level: Optional[str]  # "beginner", "intermediate", "professional"
    budget_total: Optional[float]  # total budget for bundle

    # Extracted bundle structure
    bundle_items: List[BundleItem]  # list of items to search for
    bundle_title: str  # "Cricket Starter Kit"
    bundle_description: str  # "Everything you need to start playing cricket"

    # Search results per item
    bundle_results: Dict[str, List[Any]]  # category -> products
    result_count: int

    # Display output
    formatted_output: str
    widget_json: Optional[Dict[str, Any]]
```

---

### Phase 2: LLM-Powered Bundle Analysis

#### 2.1 Bundle Identification Node

**File**: `app/graph/workflows/product_bundle_search/nodes/identify_bundle_items.py` (NEW)

This is the **core intelligence** of the workflow. Uses LLM to:

1. Understand the activity/use case
2. Identify required product categories
3. Prioritize items (essential vs optional)
4. Generate search keywords for each item

```python
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from app.services.llm import llm_service
from app.graph.workflows.product_bundle_search.types import (
    ProductBundleSearchState,
    BundleItem
)

class BundleItemSchema(BaseModel):
    """Schema for LLM output"""
    category: str = Field(description="Product category (e.g., 'cricket bat', 'running shoes')")
    purpose: str = Field(description="What this item is used for")
    keywords: str = Field(description="Search keywords to find this product")
    priority: int = Field(description="1=essential, 2=recommended, 3=optional", ge=1, le=3)
    quantity: int = Field(description="Suggested quantity", ge=1)

class BundleAnalysis(BaseModel):
    """Complete bundle analysis from LLM"""
    bundle_title: str = Field(description="Title for this bundle (e.g., 'Cricket Starter Kit')")
    bundle_description: str = Field(description="Brief description of the bundle")
    items: List[BundleItemSchema] = Field(description="List of products needed")
    user_level_detected: str = Field(
        description="Detected user level: beginner, intermediate, or professional",
        default="beginner"
    )

async def identify_bundle_items_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Uses LLM to analyze the use case and identify required products.
    This is the intelligence layer that understands user needs.
    """

    user_query = state.get("user_query", "")
    use_case = state.get("use_case", user_query)
    user_level = state.get("user_level")
    budget = state.get("budget_total")

    # Create prompt for LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert product recommendation assistant.

Your task: Analyze the user's activity/use case and identify ALL products they would need.

Guidelines:
1. **Be Comprehensive**: Include all essential items for the activity
2. **Prioritize Properly**:
   - Priority 1 (Essential): Absolute must-haves, can't do activity without these
   - Priority 2 (Recommended): Important but not critical
   - Priority 3 (Optional): Nice-to-have enhancements
3. **Consider User Level**:
   - Beginners need basics and safety items
   - Intermediate users may want quality upgrades
   - Professionals need advanced equipment
4. **Use Clear Keywords**: Generate search terms that will find the right products
5. **Be Realistic**: Suggest appropriate quantities

Examples:
- "I want to play cricket" → bat, ball, pads, gloves, helmet, shoes
- "Going camping" → tent, sleeping bag, flashlight, camping stove, backpack
- "Start home gym" → dumbbells, yoga mat, resistance bands, jump rope
- "Photography hobby" → camera, tripod, memory card, camera bag, lens

Current product database contains: electronics, sports equipment, clothing, furniture, beauty products, etc.
"""),
        ("user", """Use Case: {use_case}
User Level: {user_level}
Budget: {budget}

Identify all products needed for this use case. Return a comprehensive bundle.""")
    ])

    # Execute LLM call with structured output
    chain = prompt | llm_service.get_llm().with_structured_output(BundleAnalysis)

    result = await chain.ainvoke({
        "use_case": use_case,
        "user_level": user_level or "beginner",
        "budget": f"${budget}" if budget else "No budget specified"
    })

    # Convert to state format
    bundle_items = [
        {
            "category": item.category,
            "purpose": item.purpose,
            "keywords": item.keywords,
            "priority": item.priority,
            "quantity": item.quantity
        }
        for item in result.items
    ]

    return {
        "bundle_items": bundle_items,
        "bundle_title": result.bundle_title,
        "bundle_description": result.bundle_description,
        "user_level": result.user_level_detected
    }
```

#### 2.2 Execute Bundle Search Node

**File**: `app/graph/workflows/product_bundle_search/nodes/execute_bundle_search.py` (NEW)

Searches for products for each bundle item using existing product service:

```python
from typing import Dict, Any
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState
from app.services.db.product import product_service

async def execute_bundle_search_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Execute product searches for each bundle item.
    Reuses existing product_service.search_products_fts()
    """

    bundle_items = state.get("bundle_items", [])
    budget_total = state.get("budget_total")

    bundle_results = {}
    total_products = 0

    # Search for each bundle item
    for item in bundle_items:
        category = item["category"]
        keywords = item["keywords"]
        priority = item["priority"]

        # Build search parameters
        search_params = {
            "keywords": keywords,
            "in_stock_only": True,
            "sort_by": "relevance"
        }

        # Search for products (limit based on priority)
        limit = {
            1: 5,  # Essential: show top 5 options
            2: 3,  # Recommended: show top 3
            3: 2,  # Optional: show top 2
        }.get(priority, 3)

        products = await product_service.search_products_fts(search_params, limit=limit)

        # Store results grouped by category
        bundle_results[category] = [
            {
                "id": p.id,
                "title": p.title,
                "brand": p.brand,
                "price": p.price,
                "rating": p.rating,
                "thumbnail": p.thumbnail,
                "category": p.category,
                "priority": priority,
                "purpose": item["purpose"],
                "quantity": item["quantity"]
            }
            for p in products
        ]

        total_products += len(products)

    return {
        "bundle_results": bundle_results,
        "result_count": total_products
    }
```

#### 2.3 Format Bundle Results Node

**File**: `app/graph/workflows/product_bundle_search/nodes/format_bundle_results.py` (NEW)

```python
from typing import Dict, Any
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState

async def format_bundle_results_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Format bundle results for display.
    Creates widget JSON for frontend rendering.
    """

    bundle_results = state.get("bundle_results", {})
    bundle_title = state.get("bundle_title", "Recommended Bundle")
    bundle_description = state.get("bundle_description", "")
    result_count = state.get("result_count", 0)

    if result_count == 0:
        return {
            "formatted_output": "I couldn't find products for your use case. Please try a different activity or provide more details.",
            "widget_json": None
        }

    # Group by priority
    essential_items = {}
    recommended_items = {}
    optional_items = {}

    for category, products in bundle_results.items():
        if not products:
            continue

        priority = products[0]["priority"]

        if priority == 1:
            essential_items[category] = products
        elif priority == 2:
            recommended_items[category] = products
        else:
            optional_items[category] = products

    # Create widget JSON
    widget_json = {
        "template": "product_bundle_results",
        "payload": {
            "bundle_title": bundle_title,
            "bundle_description": bundle_description,
            "essential_items": essential_items,
            "recommended_items": recommended_items,
            "optional_items": optional_items,
            "total_categories": len(bundle_results),
            "total_products": result_count
        }
    }

    # Create text summary
    formatted_output = f"""I've prepared a **{bundle_title}** for you!

{bundle_description}

📦 **Essential Items** ({len(essential_items)} categories)
{''.join([f"- {cat}: {len(prods)} options" for cat, prods in essential_items.items()])}

{'✨ **Recommended Items** (' + str(len(recommended_items)) + ' categories)' if recommended_items else ''}
{''.join([f"- {cat}: {len(prods)} options" for cat, prods in recommended_items.items()])}

{'💎 **Optional Upgrades** (' + str(len(optional_items)) + ' categories)' if optional_items else ''}
{''.join([f"- {cat}: {len(prods)} options" for cat, prods in optional_items.items()])}

Select products from each category to create your custom bundle!"""

    return {
        "formatted_output": formatted_output,
        "widget_json": widget_json
    }
```

#### 2.4 Create Bundle Search Graph

**File**: `app/graph/workflows/product_bundle_search/graph.py` (NEW)

```python
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from app.graph.workflows.product_bundle_search.nodes.identify_bundle_items import identify_bundle_items_node
from app.graph.workflows.product_bundle_search.nodes.execute_bundle_search import execute_bundle_search_node
from app.graph.workflows.product_bundle_search.nodes.format_bundle_results import format_bundle_results_node
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState

class ProductBundleSearchGraph:
    """
    Product Bundle Search Workflow.

    Flow:
    1. Identify bundle items (LLM analyzes use case)
    2. Execute searches for each item
    3. Format and group results
    """

    @staticmethod
    def create() -> CompiledStateGraph[ProductBundleSearchState, None, ProductBundleSearchState, ProductBundleSearchState]:
        """Create the product bundle search subgraph."""

        graph = StateGraph(ProductBundleSearchState)

        # Add nodes
        graph.add_node("identify_bundle_items", identify_bundle_items_node)
        graph.add_node("execute_bundle_search", execute_bundle_search_node)
        graph.add_node("format_bundle_results", format_bundle_results_node)

        # Set entry point
        graph.set_entry_point("identify_bundle_items")

        # Linear flow: identify → search → format
        graph.add_edge("identify_bundle_items", "execute_bundle_search")
        graph.add_edge("execute_bundle_search", "format_bundle_results")
        graph.add_edge("format_bundle_results", END)

        return graph.compile()
```

#### 2.5 Create Runner Function

**File**: `app/graph/workflows/product_bundle_search/nodes/runner.py` (NEW)

```python
from app.graph.workflows.product_bundle_search.graph import ProductBundleSearchGraph
from app.types.common import GlobalState
from typing import Dict, Any

async def run_product_bundle_search(state: GlobalState, config=None) -> GlobalState:
    """Runner function for product bundle search workflow."""

    # Create workflow
    workflow = ProductBundleSearchGraph.create()

    # Prepare input state
    input_state = {
        "user_query": state.get("user_query", ""),
        "use_case": state.get("user_query", ""),  # Use query as use case
        "user_level": None,  # LLM will detect
        "budget_total": None,  # Could be extracted from query
        "conversation_history": state.get("conversation_history", []),
        "bundle_items": [],
        "bundle_results": {},
        "result_count": 0
    }

    # Execute workflow
    result = await workflow.ainvoke(input_state, config=config)

    # Update global state
    return {
        **state,
        "widget_json": result.get("widget_json"),
        "formatted_output": result.get("formatted_output"),
        "search_results": result.get("bundle_results"),  # Store for potential add-to-cart
        "workflow_completed": True
    }
```

---

### Phase 3: Integration with Base Graph

#### 3.1 Register Workflow

**File**: `app/graph/workflows/base.py`

```python
# Add import
from app.graph.workflows.product_bundle_search.nodes.runner import run_product_bundle_search

# In create_base_graph():
async def create_base_graph():
    # ... existing code ...

    # Add bundle search workflow node
    graph.add_node(NodeName.PRODUCT_BUNDLE_SEARCH_WORKFLOW, run_product_bundle_search)

    # Add to routing
    graph.add_conditional_edges(
        NodeName.ORCHESTRATOR_NODE,
        get_next_workflow,
        {
            # ... existing routes ...
            WorkflowType.PRODUCT_BUNDLE_SEARCH: NodeName.PRODUCT_BUNDLE_SEARCH_WORKFLOW,
        }
    )

    # Add edge to end
    graph.add_edge(NodeName.PRODUCT_BUNDLE_SEARCH_WORKFLOW, NodeName.OUTPUT_HANDLER)
```

#### 3.2 Update Orchestrator Mapping

**File**: `app/graph/nodes/orchestrator.py`

```python
def map_intent_to_workflow(intent: str, confidence: float) -> str:
    """Map classified intent to workflow type."""

    all_mappings = {
        # ... existing mappings ...
        "product_bundle_search": WorkflowType.PRODUCT_BUNDLE_SEARCH,
    }

    return all_mappings.get(intent, "fallback")
```

---

### Phase 4: Classifier Training

#### 4.1 Update Classifier Prompt

**File**: `app/graph/nodes/classifier.py`

Update the system prompt to recognize bundle search queries:

```python
system_prompt = """You are a query intent classifier for an e-commerce platform.

Intents:
...

**product_bundle_search**: User wants multiple related products for an activity/use case
  - Keywords: "equipment for", "what do I need for", "starter kit", "bundle", "everything I need"
  - Examples:
    * "I want to play cricket, what equipment do I need?"
    * "Show me everything I need for camping"
    * "I want to start a home gym"
    * "What should I buy for photography?"
  - Extract: activity/use case, user level (beginner/expert), budget

**product_search**: User wants specific products
  - Keywords: "find", "search", "show me", specific product names
  - Examples: "Find red shoes", "Show me Nike products"

...
"""
```

---

### Phase 5: Frontend Integration

#### 5.1 Create Bundle Display Component

**File**: `client/src/features/product-bundle-search/views/bundle-results/index.tsx` (NEW)

```typescript
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/store/chat-store";

interface BundleProduct {
  id: number;
  title: string;
  brand: string;
  price: number;
  rating: number;
  thumbnail: string;
  priority: number;
  purpose: string;
  quantity: number;
}

interface BundleResultsProps {
  payload: {
    bundle_title: string;
    bundle_description: string;
    essential_items: Record<string, BundleProduct[]>;
    recommended_items: Record<string, BundleProduct[]>;
    optional_items: Record<string, BundleProduct[]>;
  };
}

const BundleResults = ({ payload }: BundleResultsProps) => {
  const { sendMessage } = useChatStore();

  const handleAddToCart = (product: BundleProduct) => {
    sendMessage(`Add ${product.title} to my cart`);
  };

  const renderProductGroup = (
    title: string,
    items: Record<string, BundleProduct[]>,
    priorityColor: string
  ) => {
    if (Object.keys(items).length === 0) return null;

    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Badge className={priorityColor}>{title}</Badge>
        </h3>

        {Object.entries(items).map(([category, products]) => (
          <Card key={category} className="mb-4">
            <CardHeader>
              <CardTitle className="text-md">{category}</CardTitle>
              {products[0]?.purpose && (
                <p className="text-sm text-muted-foreground">
                  {products[0].purpose}
                </p>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product) => (
                  <div key={product.id} className="border rounded-lg p-3">
                    <img
                      src={product.thumbnail}
                      alt={product.title}
                      className="w-full h-32 object-cover rounded mb-2"
                    />
                    <h4 className="font-medium text-sm truncate">
                      {product.title}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {product.brand}
                    </p>
                    <div className="flex justify-between items-center mt-2">
                      <span className="font-bold">${product.price}</span>
                      <span className="text-xs">⭐ {product.rating}</span>
                    </div>
                    {product.quantity > 1 && (
                      <p className="text-xs text-blue-600">
                        Qty: {product.quantity}
                      </p>
                    )}
                    <Button
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => handleAddToCart(product)}
                    >
                      Add to Cart
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full max-w-6xl p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">{payload.bundle_title}</h2>
        <p className="text-muted-foreground">{payload.bundle_description}</p>
      </div>

      {renderProductGroup(
        "Essential Items",
        payload.essential_items,
        "bg-red-500"
      )}
      {renderProductGroup(
        "Recommended Items",
        payload.recommended_items,
        "bg-blue-500"
      )}
      {renderProductGroup(
        "Optional Upgrades",
        payload.optional_items,
        "bg-gray-500"
      )}
    </div>
  );
};

export default BundleResults;
```

#### 5.2 Register Template

**File**: `client/src/components/chat-window/signed-out-chat-window.tsx`

```typescript
// Add import
import BundleResults from "@/features/product-bundle-search/views/bundle-results";

// In getMappedTemplate function:
case "product_bundle_results":
  return <BundleResults payload={payload as any} />;
```

---

## Advanced Features (Future Enhancements)

### 1. Budget Optimization

- Distribute budget across items based on priority
- Show "budget-friendly" vs "premium" bundle options

### 2. Smart Substitutions

- If an item is out of stock, suggest alternatives
- "Similar to X but cheaper" recommendations

### 3. Bundle Templates

- Pre-defined bundles: "Cricket Beginner Kit", "Pro Camping Setup"
- Users can customize templates

### 4. Seasonal Recommendations

- Suggest weather-appropriate items
- Holiday/event-specific bundles

### 5. User History Integration

- Don't recommend items already purchased
- Consider user's past preferences

### 6. Bundle Discounts

- Apply discounts when buying complete bundles
- "Save 15% when you buy all essential items"

### 7. Comparison Mode

- Compare different bundle configurations
- Budget vs Premium comparison

---

## Testing Strategy

### Unit Tests

1. Test LLM bundle identification with various use cases
2. Test product search for each bundle item
3. Test result formatting and grouping

### Integration Tests

1. End-to-end workflow execution
2. Test with different user levels (beginner/pro)
3. Test with budget constraints

### User Acceptance Tests

1. Cricket equipment query
2. Camping gear query
3. Home gym query
4. Gaming setup query
5. Photography starter kit

---

## Implementation Timeline

| Phase       | Tasks                                | Estimated Time  |
| ----------- | ------------------------------------ | --------------- |
| **Phase 1** | Backend infrastructure, enums, state | 2-3 hours       |
| **Phase 2** | LLM nodes, search logic              | 4-5 hours       |
| **Phase 3** | Base graph integration               | 1-2 hours       |
| **Phase 4** | Classifier training                  | 1-2 hours       |
| **Phase 5** | Frontend component                   | 3-4 hours       |
| **Testing** | End-to-end testing                   | 2-3 hours       |
| **Total**   |                                      | **13-19 hours** |

---

## Success Metrics

1. **Accuracy**: LLM identifies 90%+ of relevant products for use case
2. **Completeness**: Bundles contain all essential items
3. **User Satisfaction**: Users find bundles helpful and comprehensive
4. **Conversion**: Higher conversion rate for bundle vs individual search
5. **Cart Value**: Increased average order value from bundles

---

## Summary

This workflow provides an intelligent, LLM-powered solution for recommending product bundles based on user activities. The key innovation is using the LLM to understand the use case and identify all necessary products, then leveraging existing product search infrastructure to find the best options.

The implementation is:

- ✅ **Modular**: Reuses existing services
- ✅ **Scalable**: Can handle any product category
- ✅ **Intelligent**: LLM understands context and needs
- ✅ **User-Friendly**: Clear grouping and prioritization
- ✅ **Extensible**: Easy to add features like budget optimization

Ready to implement! 🚀
