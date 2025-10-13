# Edit Cart Subgraph

## Overview

The **Edit Cart Subgraph** is a context-aware workflow that allows users to modify items in their shopping cart using natural language. It understands conversational references like "that shirt", "the red one", or "the last item I added" by analyzing conversation history.

## Features

### Context-Aware Item Recognition

The subgraph uses conversation history to understand references:

- **Temporal references**: "the last one", "that item I just added"
- **Descriptive references**: "the red one", "that shirt", "the Nike shoes"
- **Implicit references**: "it", "that", "those"

### Supported Edit Operations

1. **Remove Items**

   - Delete specific items from the cart
   - Examples: "Remove that shirt", "Delete the red one"

2. **Update Quantity**

   - Change the number of items
   - Examples: "Make it 3 instead of 2", "Change to 5 pieces"

3. **Update Properties**

   - Modify item attributes like size and color
   - Examples: "Change that to size Large", "Make it blue"

4. **Replace Items**
   - Swap one product for another
   - Examples: "Replace with the blue one", "Change to Adidas brand"

## Workflow Architecture

### State: `EditCartState`

```python
class EditCartState(CommonState, AuthState):
    # Edit operation details
    edit_type: str | None  # "remove", "update_quantity", "update_properties", "replace"
    target_product_reference: str | None

    # Item identification
    matched_cart_item: Dict[str, Any] | None
    cart_item_id: int | None

    # Edit parameters
    new_quantity: int | None
    new_size: str | None
    new_color: str | None
    replacement_product: Dict[str, Any] | None

    # Cart data
    cart_details: List[CartItemWithProductDetails] | None
    updated_cart_details: List[CartItemWithProductDetails] | None

    # Workflow control
    edit_success: bool
    workflow_output_text: str | None
    workflow_output_json: Dict[str, Any] | None
    error_message: str | None
```

### Node Flow

```
┌─────────────────────────┐
│  Extract Edit Details   │  ← Extracts edit intent and parameters
│  (LLM + Context)        │     from user message
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Identify Cart Item     │  ← Matches user reference to actual
│  (LLM + Cart Data)      │     cart item using smart matching
└──────────┬──────────────┘
           │
           ▼
     ┌────┴────┐
     │ Found?  │
     └────┬────┘
          │
    ┌─────┴─────┐
   Yes          No
    │            │
    ▼            ▼
┌──────────┐  ┌────────────────┐
│  Apply   │  │ Handle Failure │
│  Edit    │  └────────────────┘
└────┬─────┘
     │
     ▼
┌────┴────┐
│ Success?│
└────┬────┘
     │
┌────┴─────┐
│          │
▼          ▼
Success  Failure
Handler  Handler
```

## Nodes

### 1. `extract_edit_details`

**Purpose**: Extract edit operation details from user's natural language request

**Key Features**:

- Uses LLM with conversation history for context awareness
- Classifies edit type accurately
- Resolves ambiguous references using conversation context
- Extracts all relevant parameters (quantity, size, color, replacement details)

**Input**: User message + conversation history
**Output**: Edit type, target reference, and parameters

### 2. `identify_cart_item`

**Purpose**: Match user's reference to an actual cart item

**Key Features**:

- Retrieves current cart items with full product details
- Uses LLM to perform smart matching
- Considers product name, brand, size, color, and temporal aspects
- Returns confidence level and reasoning

**Input**: Target reference + current cart items
**Output**: Matched cart item ID

### 3. `apply_cart_edit`

**Purpose**: Execute the edit operation

**Supported Operations**:

- **Remove**: Deletes item using `cart_service.remove_cart_item_by_cart_item_id()`
- **Update Quantity**: Updates using `cart_service.update_item_quantity()`
- **Update Properties**: Updates using `cart_service.update_cart_item_properties()`
- **Replace**: Searches for new product, removes old, adds new

**Input**: Edit parameters + matched cart item
**Output**: Success/failure status + updated cart

### 4. `handle_edit_success`

**Purpose**: Format successful response with updated cart information

**Output**:

- User-friendly success message
- Updated cart summary (total items, total amount)
- Full cart details in JSON format

### 5. `handle_edit_failure`

**Purpose**: Format helpful error messages

**Output**:

- User-friendly error explanation
- Suggestions for resolution
- Error details in JSON format

## Database Operations

### New Methods Added to `CartService`

```python
async def remove_cart_item_by_cart_item_id(
    user_id: int,
    cart_item_id: int
) -> bool:
    """Remove a specific cart item by its cart_item_id."""

async def update_cart_item_properties(
    user_id: int,
    cart_item_id: int,
    size: str | None = None,
    color: str | None = None
) -> Optional[CartItem]:
    """Update properties (size, color) of a cart item."""
```

## Usage Examples

### Example 1: Remove Item

```
User: "Add Summer Breeze T-shirt by Nike to cart"
Bot: "Added Summer Breeze T-shirt to your cart"
User: "Actually, remove that shirt"
Bot: "Successfully removed Summer Breeze T-shirt from your cart."
```

### Example 2: Update Quantity

```
User: "Add 2 Blue Jeans to cart"
Bot: "Added 2 Blue Jeans to your cart"
User: "Make it 3 instead of 2"
Bot: "Updated Blue Jeans quantity to 3."
```

### Example 3: Update Properties

```
User: "Add Red Dress in size M to cart"
Bot: "Added Red Dress (M) to your cart"
User: "Change that to size Large"
Bot: "Updated Red Dress - changed size to Large."
```

### Example 4: Replace Item

```
User: "Add Blue Sweater by Nike to cart"
Bot: "Added Blue Sweater to your cart"
User: "Replace it with the Red Sweater by Adidas"
Bot: "Successfully replaced Blue Sweater with Red Sweater."
```

## Integration Guide

### 1. Register Workflow

Add to your workflow registry (likely in orchestrator or main graph):

```python
from app.graph.workflows.order_management.subgraphs.edit_cart.graph import EditCartGraph

# Create the subgraph
edit_cart_graph = EditCartGraph.create()

# Add as a node to your main graph
main_graph.add_node(
    NodeName.EDIT_CART_WORKFLOW,
    edit_cart_graph
)
```

### 2. Add Authentication Wrapper

Since cart operations require authentication, wrap with auth middleware:

```python
from app.graph.workflows.auth_middleware.graph import AuthMiddlewareGraph

# Create auth-protected version
auth_protected_edit_cart = AuthMiddlewareGraph.create(
    protected_workflow=edit_cart_graph,
    workflow_name="edit_cart"
)

main_graph.add_node(
    NodeName.AUTH_PROTECTED_EDIT_CART_WORKFLOW,
    auth_protected_edit_cart
)
```

### 3. Update Classifier

Add "edit_cart" intent to your classifier model's training data:

```python
# In classifier training/config
intents = {
    # ... existing intents ...
    "edit_cart": [
        "remove that shirt",
        "change the size to large",
        "make it 3 instead of 2",
        "replace with blue one",
        "update quantity to 5",
        "delete the red one",
        "change color to black"
    ]
}
```

### 4. Update Orchestrator Routing

Add routing logic to direct edit_cart intents to the workflow:

```python
def route_to_workflow(state):
    intent = state.get("intent")

    if intent == IntentType.EDIT_CART:
        return NodeName.AUTH_PROTECTED_EDIT_CART_WORKFLOW
    # ... other routing logic ...
```

## Error Handling

The subgraph handles various error scenarios gracefully:

1. **Empty Cart**: "Your cart is empty. There are no items to edit."
2. **Item Not Found**: "I couldn't identify which item you're referring to. Could you be more specific?"
3. **Authentication**: "You need to be logged in to edit your cart."
4. **Invalid Quantity**: "Please specify a valid quantity (must be greater than 0)."
5. **Product Not Found**: "Could not find replacement product: [product name]"

## Response Format

### Success Response

```json
{
  "success": true,
  "edit_type": "update_quantity",
  "edited_item": {
    "product_name": "Blue Jeans",
    "previous_quantity": 2,
    "previous_size": "M",
    "previous_color": "Blue"
  },
  "cart_summary": {
    "total_items": 3,
    "total_amount": 89.97,
    "items": [
      {
        "id": 1,
        "product_id": 123,
        "product_name": "Blue Jeans",
        "brand": "Levi's",
        "quantity": 3,
        "size": "M",
        "color": "Blue",
        "unit_price": 29.99,
        "total_price": 89.97,
        "thumbnail": "https://..."
      }
    ]
  }
}
```

### Failure Response

```json
{
  "success": false,
  "error": "Could not identify which item you're referring to",
  "edit_type": "remove",
  "target_reference": "that thing",
  "suggestions": [
    "View your cart to see all items",
    "Try being more specific about which item you want to edit",
    "Make sure the item is actually in your cart"
  ]
}
```

## Testing Recommendations

1. **Context Resolution Tests**

   - Test with various reference types ("that", "the one", "the last one")
   - Test with temporal references
   - Test with descriptive references

2. **Edit Operation Tests**

   - Test all four edit types (remove, update_quantity, update_properties, replace)
   - Test edge cases (quantity = 0, invalid size, product not found)
   - Test with multiple items in cart

3. **Error Scenario Tests**

   - Empty cart
   - Ambiguous references
   - Non-existent products
   - Unauthenticated users

4. **Integration Tests**
   - Test with real conversation history
   - Test chaining multiple edits
   - Test with view_cart workflow

## Performance Considerations

- **LLM Calls**: The workflow makes 2 LLM calls (extract + identify), which may add latency
- **Cart Queries**: Fetches full cart with product details for matching
- **Optimization Opportunities**:
  - Cache recent cart state for faster matching
  - Use embeddings for product matching instead of LLM call
  - Batch multiple edits if user requests them together

## Future Enhancements

1. **Bulk Operations**: Support editing multiple items at once
2. **Undo/Redo**: Allow users to undo recent cart edits
3. **Smart Suggestions**: Suggest alternative sizes/colors when replacing
4. **Price Tracking**: Notify users of price changes when editing
5. **Wishlist Integration**: Move items to wishlist instead of deletion

## Dependencies

- `langgraph`: State graph framework
- `langchain`: LLM integration
- `pydantic`: Data validation
- Cart service and database layer
- Product service for replacements
- Authentication middleware

## Related Workflows

- **add_to_cart**: For adding new items
- **view_cart**: For viewing current cart
- **delete_from_cart**: For bulk deletion
- **checkout**: For completing purchase
