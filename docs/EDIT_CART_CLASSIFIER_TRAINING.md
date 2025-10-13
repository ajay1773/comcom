# Edit Cart Intent - Classifier Training Examples

## Overview

This document contains training examples for the intent classifier to recognize `edit_cart` intents. Add these examples to your classifier model's training data.

## Intent: `edit_cart`

### Remove Operations (Delete Item)

**Keywords**: remove, delete, take out, get rid of, discard, drop

```
"Remove that shirt"
"Delete the red one"
"Take that out of my cart"
"Get rid of the Nike shoes"
"Remove the item I just added"
"Delete that product"
"Take out the last thing"
"Remove the sweater"
"Get that out of my cart"
"Delete the blue jeans"
"Remove what I just put in"
"Take the shirt out"
"Delete the last item"
"Remove those shoes"
"Get rid of that"
"Discard the red dress"
"Drop the Nike shirt"
"Remove the jacket"
"Delete the product I just added"
"Take that item out"
```

### Update Quantity

**Keywords**: make it, change to, update to, I want, adjust, increase, decrease, more, fewer

```
"Make it 3 instead of 2"
"Change quantity to 5"
"I want 2 of those"
"Update to 4 items"
"Make that 3"
"Change it to 1"
"I want 5 instead"
"Increase to 10"
"Decrease to 2"
"Make it 2 more"
"Change the quantity to 3"
"I need 4 of them"
"Update quantity to 2"
"Make that 5 pieces"
"Change to 3 items"
"I want 3 instead of 1"
"Adjust quantity to 4"
"Make it 1 less"
"Change to 2"
"I need more, make it 5"
```

### Update Properties (Size, Color, etc.)

**Keywords**: change size, change color, make it, switch to, different size/color

```
"Change that to size large"
"Make it blue instead"
"Switch to size XL"
"Change the size to medium"
"I want it in red"
"Make that size small"
"Change color to black"
"Switch to large"
"Make it a different size"
"Change to size 10"
"I want it in blue instead"
"Make that XL"
"Change the color to white"
"Switch size to medium"
"Make it size 8"
"Change to red color"
"I need it in large"
"Make that blue"
"Change size to small"
"Switch to black"
```

### Replace Operations

**Keywords**: replace, swap, change to different, instead of, switch product

```
"Replace it with the blue one"
"Swap for the Adidas version"
"Change to a different brand"
"Replace with the red sweater"
"Switch to Nike instead"
"Get the blue one instead"
"Replace that with the other one"
"Swap for different product"
"Change to the Adidas shirt"
"Replace with the large size"
"Switch to the premium version"
"Get the red one instead of blue"
"Replace with better quality"
"Swap for the discounted item"
"Change to the other brand"
"Replace it with something else"
"Switch to the blue version"
"Get the Nike one instead"
"Replace with the cheaper option"
"Swap for the red model"
```

### Mixed/Ambiguous (Still edit_cart)

**Keywords**: actually, wait, change mind, instead

```
"Actually, I don't want that"
"Wait, change that"
"Make it different"
"I changed my mind about the shirt"
"Actually, different size"
"Wait, I want blue instead"
"Can you change that?"
"Actually make it 2"
"Wait, remove that"
"I want to modify my cart"
"Can I change the size?"
"Actually, I need large"
"Wait, different color"
"Change my cart"
"Modify that item"
"Update my cart"
"Fix that order"
"Adjust my cart"
"Edit the cart"
"Change what I ordered"
```

## Classifier Configuration

### Intent Priority

When a message contains edit-related keywords AND references to cart/items, classify as `edit_cart`.

### Context Signals

Strong indicators of `edit_cart` intent:

1. **Recent cart activity**: User just added something to cart
2. **Edit keywords**: "change", "make it", "replace", "remove"
3. **Reference words**: "that", "it", "the one", "last item"
4. **Quantity numbers**: "make it 3", "2 instead of 1"
5. **Property words**: "size", "color", "large", "small", "red", "blue"

### Differentiation from Similar Intents

#### vs. `delete_from_cart` (bulk deletion)

- `delete_from_cart`: "Clear my cart", "Empty cart", "Delete everything"
- `edit_cart`: "Remove that shirt", "Delete the red one" (specific item)

#### vs. `add_to_cart`

- `add_to_cart`: "Add blue shirt", "Put red dress in cart"
- `edit_cart`: "Change it to blue", "Make that red instead" (modifying existing)

#### vs. `view_cart`

- `view_cart`: "Show my cart", "What's in my cart?"
- `edit_cart`: "Change that item", "Remove the shirt" (action-oriented)

## Example Training Set Structure

```python
training_examples = {
    "edit_cart": [
        # Remove
        {"text": "Remove that shirt", "label": "edit_cart"},
        {"text": "Delete the red one", "label": "edit_cart"},
        {"text": "Take that out", "label": "edit_cart"},

        # Update quantity
        {"text": "Make it 3 instead of 2", "label": "edit_cart"},
        {"text": "I want 5 of those", "label": "edit_cart"},
        {"text": "Change quantity to 2", "label": "edit_cart"},

        # Update properties
        {"text": "Change to size large", "label": "edit_cart"},
        {"text": "Make it blue", "label": "edit_cart"},
        {"text": "Switch to XL", "label": "edit_cart"},

        # Replace
        {"text": "Replace with the blue one", "label": "edit_cart"},
        {"text": "Swap for Adidas", "label": "edit_cart"},
        {"text": "Get the red one instead", "label": "edit_cart"},

        # Ambiguous
        {"text": "Actually, change that", "label": "edit_cart"},
        {"text": "Wait, make it different", "label": "edit_cart"},
        {"text": "I changed my mind", "label": "edit_cart"},
    ]
}
```

## Confidence Thresholds

### High Confidence (>0.85)

- Explicit edit keywords + item reference
- Examples: "Remove that shirt", "Change size to large"

### Medium Confidence (0.6-0.85)

- Implicit edit intent with context
- Examples: "Make it blue", "I want 3"

### Low Confidence (<0.6)

- Ambiguous without context
- Examples: "Change it", "Different one"
- Action: Request clarification

## Testing Strategy

### Test Cases

1. **After adding item**:

   ```
   User: "Add blue shirt"
   Bot: "Added blue shirt"
   User: "Remove that" → Should be edit_cart
   ```

2. **Multiple items in cart**:

   ```
   User: [has 3 items in cart]
   User: "Remove the Nike one" → Should be edit_cart
   ```

3. **Property modification**:

   ```
   User: "Add red dress size M"
   Bot: "Added red dress (M)"
   User: "Make it large" → Should be edit_cart
   ```

4. **Quantity adjustment**:
   ```
   User: "Add 2 jeans"
   Bot: "Added 2 jeans"
   User: "Actually make it 3" → Should be edit_cart
   ```

## Integration Notes

### Required Classifier Updates

1. **Add Intent Type**:

   ```python
   from app.core.enums import IntentType
   # IntentType.EDIT_CART already added ✓
   ```

2. **Update Intent Mapping**:

   ```python
   # In orchestrator.py - already added ✓
   ecommerce_workflows = {
       ...
       "edit_cart": "edit_cart",
       ...
   }
   ```

3. **Train Classifier**:
   - Add training examples above to your classifier training script
   - Retrain the model with new examples
   - Test classification accuracy
   - Deploy updated model

### Minimum Training Data

- **Recommended**: 100+ examples per edit type (400+ total)
- **Minimum**: 20+ examples per edit type (80+ total)
- **Current**: 100+ examples provided in this document

## Validation

### Positive Tests (Should classify as edit_cart)

```python
assert classify("Remove that shirt") == "edit_cart"
assert classify("Make it size large") == "edit_cart"
assert classify("Change to 3 instead") == "edit_cart"
assert classify("Replace with blue one") == "edit_cart"
```

### Negative Tests (Should NOT be edit_cart)

```python
assert classify("Add blue shirt") == "add_to_cart"
assert classify("Show my cart") == "view_cart"
assert classify("Clear cart") == "delete_from_cart"
assert classify("Checkout now") == "checkout"
```

## Model Performance Targets

- **Accuracy**: >90% on edit_cart classification
- **Precision**: >85% (few false positives)
- **Recall**: >90% (catch most edit intents)
- **F1 Score**: >88%

## Notes

- Start with high-quality examples from this document
- Monitor misclassifications in production
- Add edge cases to training set over time
- Re-train periodically with new data

---

**Last Updated**: October 12, 2025  
**Training Examples**: 100+  
**Status**: Ready for classifier integration
