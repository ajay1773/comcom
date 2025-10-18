# Product Bundle Widget Event Implementation

## Overview

This document describes the implementation of the widget event system for product bundle search results, enabling seamless communication between the backend workflow and the frontend UI components.

## Implementation Summary

### 1. Backend Changes

#### 1.1 Widget Event Type Addition (`app/services/widget_events.py`)

Added a new event type to the `WidgetEventType` enum:

```python
class WidgetEventType(str, Enum):
    # ... existing event types
    PRODUCT_BUNDLE_RESULTS = "product_bundle_results"
    # ... other event types
```

#### 1.2 Event Emission in Format Node (`app/graph/workflows/product_bundle_search/nodes/format_bundle_results.py`)

Added widget event emission in the `format_bundle_results_node`:

```python
from app.services.widget_events import widget_event_emitter, WidgetEventType

async def format_bundle_results_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    # ... existing logic to prepare bundle results ...

    # Emit widget event for frontend
    widget_event_emitter.emit(
        WidgetEventType.PRODUCT_BUNDLE_RESULTS,
        {
            "bundle_title": bundle_title,
            "bundle_description": bundle_description,
            "essential_items": essential_items,
            "recommended_items": recommended_items,
            "optional_items": optional_items,
            "total_categories": len(bundle_results),
            "total_products": result_count,
            "success_message": response_text,
            "suggested_actions": [
                "Add to cart",
                "View details",
                "Continue shopping"
            ]
        }
    )

    return {
        "workflow_output_text": response_text,
        "workflow_output_json": widget_json
    }
```

### 2. Frontend Changes

#### 2.1 Signed-In Chat Window (`client/src/components/chat-window/signed-in-chat-window.tsx`)

1. **Import the BundleResults component:**

```typescript
import BundleResults from "@/features/product-bundle-search/views/bundle-results";
```

2. **Add case to `getMappedTemplate` function:**

```typescript
case "product_bundle_results":
  return (
    <BundleResults
      payload={
        payload as {
          bundle_title: string;
          bundle_description: string;
          essential_items: Record<string, any[]>;
          recommended_items: Record<string, any[]>;
          optional_items: Record<string, any[]>;
          total_categories: number;
          total_products: number;
        }
      }
    />
  );
```

#### 2.2 Signed-Out Chat Window (`client/src/components/chat-window/signed-out-chat-window.tsx`)

Similar changes were made to the signed-out version to ensure consistent experience for all users.

### 3. Existing Component Structure

The `BundleResults` component (`client/src/features/product-bundle-search/views/bundle-results/index.tsx`) was already well-designed and didn't require any modifications. It properly handles:

- **Bundle metadata**: Title and description
- **Priority-based grouping**: Essential, Recommended, and Optional items
- **Category organization**: Products grouped by category within each priority level
- **Product cards**: Rich product display with images, pricing, ratings, and add-to-cart functionality
- **Interactive actions**: Integrates with chat store to send messages for cart operations

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Backend Workflow                              │
├─────────────────────────────────────────────────────────────────┤
│  1. identify_bundle_items_node                                  │
│     └─> Identifies items needed for the bundle                  │
│                                                                  │
│  2. execute_bundle_search_node                                  │
│     └─> Searches database for products matching each item       │
│                                                                  │
│  3. format_bundle_results_node                                  │
│     ├─> Organizes results by priority (essential/recommended/   │
│     │   optional)                                                │
│     ├─> Generates natural language response via LLM             │
│     └─> EMITS WIDGET EVENT with structured payload              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ SSE Stream
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Application                          │
├─────────────────────────────────────────────────────────────────┤
│  1. Chat Store receives widget_event                            │
│     └─> Updates widgetJson state                                │
│                                                                  │
│  2. ChatWindow component re-renders                             │
│     └─> Calls getMappedTemplate with new payload                │
│                                                                  │
│  3. BundleResults component displays                            │
│     ├─> Shows bundle title and description                      │
│     ├─> Renders essential items section                         │
│     ├─> Renders recommended items section                       │
│     ├─> Renders optional items section                          │
│     └─> Provides "Add to Cart" buttons for each product         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Payload Structure

The widget event payload follows this structure:

```typescript
{
  bundle_title: string;              // e.g., "Cricket Starter Kit"
  bundle_description: string;        // e.g., "Everything you need to start playing cricket"
  essential_items: {                 // Priority 1 items
    [category: string]: Array<{
      id: number;
      title: string;
      brand: string;
      price: number;
      rating: number;
      thumbnail: string;
      priority: number;
      purpose: string;
      quantity: number;
    }>
  };
  recommended_items: {               // Priority 2 items
    [category: string]: Product[];
  };
  optional_items: {                  // Priority 3 items
    [category: string]: Product[];
  };
  total_categories: number;
  total_products: number;
  success_message: string;           // LLM-generated friendly message
  suggested_actions: string[];       // Array of action suggestions
}
```

## Key Features

### 1. Priority-Based Organization

Products are automatically grouped into three priority levels:

- **Essential Items** (Priority 1): Must-have items for the activity
- **Recommended Items** (Priority 2): Highly suggested additions
- **Optional Items** (Priority 3): Nice-to-have upgrades

### 2. Category Grouping

Within each priority level, products are grouped by category for easy browsing.

### 3. Natural Language Response

The LLM generates a friendly, conversational message that:

- Acknowledges the user's request with enthusiasm
- Explains the bundle organization
- Encourages exploration
- Maintains a warm, human tone

### 4. Interactive UI

- Each product has an "Add to Cart" button
- Clicking the button sends a message to the chat system
- Seamless integration with existing cart management workflow

### 5. No Results Handling

When no products are found, the system:

- Uses LLM to generate a polite, helpful message
- Suggests alternative actions
- Maintains a positive, encouraging tone

## Benefits of This Approach

1. **Decoupled Architecture**: Backend and frontend communicate through events
2. **Reusability**: Widget event system can be extended for other features
3. **Consistent UX**: Same pattern as other widget events (cart, search, etc.)
4. **Type Safety**: Strong typing on both backend and frontend
5. **Natural Language**: LLM-generated messages feel conversational and helpful
6. **Scalability**: Easy to add more bundle types or customize behavior

## Testing Recommendations

### Backend Testing

1. Test with various use cases (sports, hobbies, activities)
2. Verify proper priority assignment
3. Test no-results scenario
4. Validate LLM response quality

### Frontend Testing

1. Test bundle display with different product counts
2. Verify "Add to Cart" functionality
3. Test responsive layout
4. Validate empty state handling

### Integration Testing

1. End-to-end bundle search workflow
2. Event emission and reception
3. Multiple bundle searches in same conversation
4. Error handling and recovery

## Future Enhancements

1. **Bundle Customization**: Allow users to modify bundle composition
2. **Price Filtering**: Show bundles within budget constraints
3. **Comparison**: Compare different bundle configurations
4. **Saved Bundles**: Allow users to save and retrieve bundles
5. **Bundle Analytics**: Track popular bundle combinations
6. **Smart Recommendations**: Learn from user preferences

## Related Documentation

- [Product Bundle Workflow Overview](./PRODUCT_BUNDLE_WORKFLOW_OVERVIEW.md)
- [Widget Events System](../app/services/widget_events.py)
- [Bundle Implementation Summary](./BUNDLE_IMPLEMENTATION_SUMMARY.md)
