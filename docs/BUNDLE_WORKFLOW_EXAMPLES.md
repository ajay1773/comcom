# Bundle Workflow - Examples & Test Cases

## Example Use Cases with Expected Outputs

### Example 1: Cricket Equipment

#### User Query

```
"I want to play cricket, do you have equipment for it?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Cricket Starter Kit",
  "bundle_description": "Complete equipment set for cricket beginners",
  "user_level_detected": "beginner",
  "items": [
    {
      "category": "Cricket Bat",
      "purpose": "For batting and scoring runs",
      "keywords": "cricket bat beginner wood",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Cricket Ball",
      "purpose": "For bowling and practice",
      "keywords": "cricket ball leather",
      "priority": 1,
      "quantity": 2
    },
    {
      "category": "Batting Pads",
      "purpose": "Leg protection while batting",
      "keywords": "cricket pads leg guards",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Cricket Gloves",
      "purpose": "Hand protection for batting",
      "keywords": "cricket batting gloves",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Cricket Helmet",
      "purpose": "Head protection for batsman",
      "keywords": "cricket helmet safety",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Cricket Shoes",
      "purpose": "Proper grip on field",
      "keywords": "cricket shoes spikes",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Kit Bag",
      "purpose": "Carrying all equipment",
      "keywords": "cricket kit bag sports bag",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

#### Final Display

```
I've prepared a Cricket Starter Kit for you!

Complete equipment set for cricket beginners

📦 Essential Items (3 categories)
- Cricket Bat: 5 options ($45 - $150)
- Cricket Ball: 5 options ($8 - $25)
- Batting Pads: 5 options ($35 - $120)

✨ Recommended Items (3 categories)
- Cricket Gloves: 3 options ($20 - $60)
- Cricket Helmet: 3 options ($40 - $180)
- Cricket Shoes: 3 options ($55 - $140)

💎 Optional Upgrades (1 category)
- Kit Bag: 2 options ($30 - $80)

Select products from each category to create your custom bundle!
```

---

### Example 2: Camping Trip

#### User Query

```
"I'm going camping next weekend, what should I buy?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Weekend Camping Essentials",
  "bundle_description": "Everything you need for a safe and comfortable camping trip",
  "user_level_detected": "beginner",
  "items": [
    {
      "category": "Camping Tent",
      "purpose": "Shelter for overnight stay",
      "keywords": "camping tent 2 person waterproof",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Sleeping Bag",
      "purpose": "Warm sleeping during night",
      "keywords": "sleeping bag camping warm",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Flashlight",
      "purpose": "Light source for night",
      "keywords": "flashlight camping LED rechargeable",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Camping Stove",
      "purpose": "Cooking meals outdoors",
      "keywords": "camping stove portable gas",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Backpack",
      "purpose": "Carrying camping gear",
      "keywords": "hiking backpack camping 40L",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "First Aid Kit",
      "purpose": "Emergency medical supplies",
      "keywords": "first aid kit camping outdoor",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Portable Charger",
      "purpose": "Charging devices outdoors",
      "keywords": "power bank portable charger solar",
      "priority": 3,
      "quantity": 1
    },
    {
      "category": "Camping Chair",
      "purpose": "Comfortable seating",
      "keywords": "camping chair folding portable",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

---

### Example 3: Home Gym Setup

#### User Query

```
"I want to start working out at home, what equipment do I need?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Home Gym Starter Pack",
  "bundle_description": "Essential fitness equipment for home workouts",
  "user_level_detected": "beginner",
  "items": [
    {
      "category": "Yoga Mat",
      "purpose": "Floor exercises and stretching",
      "keywords": "yoga mat exercise non-slip thick",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Dumbbells",
      "purpose": "Strength training and toning",
      "keywords": "dumbbells adjustable weight set",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Resistance Bands",
      "purpose": "Muscle building and flexibility",
      "keywords": "resistance bands exercise loop set",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Jump Rope",
      "purpose": "Cardio and warm-up",
      "keywords": "jump rope fitness speed rope",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Foam Roller",
      "purpose": "Muscle recovery and massage",
      "keywords": "foam roller massage recovery",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Exercise Ball",
      "purpose": "Core strengthening",
      "keywords": "exercise ball stability yoga ball",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Kettlebell",
      "purpose": "Full body workouts",
      "keywords": "kettlebell cast iron weight",
      "priority": 3,
      "quantity": 1
    },
    {
      "category": "Pull-up Bar",
      "purpose": "Upper body strength",
      "keywords": "pull up bar doorway home gym",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

---

### Example 4: Photography Hobby

#### User Query

```
"I want to start photography as a hobby, what should I get?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Photography Starter Kit",
  "bundle_description": "Essential gear to begin your photography journey",
  "user_level_detected": "beginner",
  "items": [
    {
      "category": "DSLR Camera",
      "purpose": "Main photography tool",
      "keywords": "DSLR camera beginner kit canon nikon",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Memory Card",
      "purpose": "Storing photos",
      "keywords": "SD card memory card 64GB high speed",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Camera Bag",
      "purpose": "Protecting camera equipment",
      "keywords": "camera bag DSLR backpack padded",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Tripod",
      "purpose": "Stable shots and long exposure",
      "keywords": "tripod camera portable lightweight",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Camera Lens",
      "purpose": "Different shooting perspectives",
      "keywords": "camera lens 50mm portrait",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Lens Cleaning Kit",
      "purpose": "Maintaining equipment",
      "keywords": "lens cleaning kit camera care",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "External Flash",
      "purpose": "Better lighting control",
      "keywords": "camera flash speedlight external",
      "priority": 3,
      "quantity": 1
    },
    {
      "category": "Photography Book",
      "purpose": "Learning techniques",
      "keywords": "photography book beginner guide tutorial",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

---

### Example 5: Gaming Setup

#### User Query

```
"I want to setup a gaming station, what all do I need?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Complete Gaming Setup",
  "bundle_description": "Everything needed for an immersive gaming experience",
  "user_level_detected": "intermediate",
  "items": [
    {
      "category": "Gaming Monitor",
      "purpose": "High refresh rate display",
      "keywords": "gaming monitor 144hz 1ms response",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Gaming Mouse",
      "purpose": "Precise control and accuracy",
      "keywords": "gaming mouse wireless RGB",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Gaming Keyboard",
      "purpose": "Responsive mechanical keys",
      "keywords": "gaming keyboard mechanical RGB backlit",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Gaming Headset",
      "purpose": "Immersive audio and communication",
      "keywords": "gaming headset surround sound microphone",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Gaming Chair",
      "purpose": "Comfortable extended gaming",
      "keywords": "gaming chair ergonomic office chair",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Mouse Pad",
      "purpose": "Smooth mouse movement",
      "keywords": "gaming mouse pad XXL extended",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Webcam",
      "purpose": "Streaming and video calls",
      "keywords": "webcam 1080p streaming gaming",
      "priority": 3,
      "quantity": 1
    },
    {
      "category": "LED Strip Lights",
      "purpose": "Ambient setup lighting",
      "keywords": "LED strip lights RGB gaming room",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

---

### Example 6: Cooking/Baking Essentials

#### User Query

```
"I'm learning to bake, what equipment should I buy?"
```

#### LLM Bundle Identification Output

```json
{
  "bundle_title": "Baking Essentials Kit",
  "bundle_description": "Must-have tools for beginner bakers",
  "user_level_detected": "beginner",
  "items": [
    {
      "category": "Mixing Bowls",
      "purpose": "Mixing ingredients",
      "keywords": "mixing bowls set stainless steel nesting",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Measuring Cups",
      "purpose": "Accurate ingredient measurement",
      "keywords": "measuring cups spoons set baking",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Baking Pan",
      "purpose": "Baking cakes and brownies",
      "keywords": "baking pan non-stick rectangular",
      "priority": 1,
      "quantity": 1
    },
    {
      "category": "Hand Mixer",
      "purpose": "Mixing batter and cream",
      "keywords": "hand mixer electric kitchen beater",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Silicone Spatula",
      "purpose": "Scraping and mixing",
      "keywords": "silicone spatula set heat resistant",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Cooling Rack",
      "purpose": "Cooling baked goods",
      "keywords": "cooling rack baking wire grid",
      "priority": 2,
      "quantity": 1
    },
    {
      "category": "Rolling Pin",
      "purpose": "Rolling dough",
      "keywords": "rolling pin wooden baking",
      "priority": 3,
      "quantity": 1
    },
    {
      "category": "Piping Bags Set",
      "purpose": "Decorating cakes",
      "keywords": "piping bags tips set cake decorating",
      "priority": 3,
      "quantity": 1
    }
  ]
}
```

---

## Edge Cases to Handle

### Edge Case 1: Very Specific Use Case

**Query**: "I need equipment for underwater macro photography"

**Expected Behavior**:

- LLM should identify niche items
- May return fewer results if products don't exist
- Suggest alternatives or broader categories

### Edge Case 2: Budget Constraint

**Query**: "I want to play cricket but my budget is only $100"

**Expected Behavior**:

- Prioritize essential items only
- Filter products by price
- Show affordable alternatives

### Edge Case 3: Professional Level

**Query**: "I'm a professional photographer, what advanced equipment do you have?"

**Expected Behavior**:

- Focus on professional-grade items
- Higher priority to advanced features
- Skip basic beginner items

### Edge Case 4: Partial Bundle

**Query**: "I already have a cricket bat, what else do I need?"

**Expected Behavior**:

- Exclude already-owned items
- Focus on complementary products
- Adjust bundle accordingly

### Edge Case 5: No Products Found

**Query**: "I want to learn quantum computing, what tools do I need?"

**Expected Behavior**:

- Gracefully handle no results
- Suggest related categories available
- Provide fallback message

---

## Testing Checklist

### Functional Tests

- [ ] LLM correctly identifies bundle items
- [ ] All priorities assigned correctly (1-3)
- [ ] Search finds relevant products for each item
- [ ] Results grouped by priority
- [ ] Widget JSON formatted correctly
- [ ] Frontend displays all sections

### Edge Case Tests

- [ ] Handle budget constraints
- [ ] Handle user level variations
- [ ] Handle no results gracefully
- [ ] Handle partial bundles
- [ ] Handle very specific use cases

### Integration Tests

- [ ] End-to-end workflow execution
- [ ] Classifier routes to bundle workflow
- [ ] Add-to-cart works from bundle
- [ ] Multiple bundle searches in same session

### Performance Tests

- [ ] Response time < 5 seconds
- [ ] Handles 10+ bundle items
- [ ] LLM call completes within 2 seconds
- [ ] Database queries optimized

---

## Sample Frontend Display

```
┌────────────────────────────────────────────────────────────┐
│  Cricket Starter Kit                                        │
│  Complete equipment set for cricket beginners               │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  🔴 Essential Items                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Cricket Bat - For batting and scoring runs        │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │    │
│  │  │ MRF Bat  │ │ SS Bat   │ │ Kookabu. │          │    │
│  │  │ $89.99   │ │ $124.99  │ │ $149.99  │          │    │
│  │  │ ⭐ 4.5   │ │ ⭐ 4.7   │ │ ⭐ 4.8   │          │    │
│  │  │ [Add]    │ │ [Add]    │ │ [Add]    │          │    │
│  │  └──────────┘ └──────────┘ └──────────┘          │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Cricket Ball - For bowling and practice           │    │
│  │  Qty: 2 recommended                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │    │
│  │  │ SG Ball  │ │ Kookabu. │ │ Dukes    │          │    │
│  │  │ $12.99   │ │ $18.99   │ │ $24.99   │          │    │
│  │  │ ⭐ 4.3   │ │ ⭐ 4.6   │ │ ⭐ 4.8   │          │    │
│  │  │ [Add]    │ │ [Add]    │ │ [Add]    │          │    │
│  │  └──────────┘ └──────────┘ └──────────┘          │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘

[Similar sections for Recommended and Optional items...]

┌────────────────────────────────────────────────────────────┐
│  Bundle Summary                                             │
│  • 3 Essential categories (14 products)                     │
│  • 3 Recommended categories (9 products)                    │
│  • 1 Optional category (2 products)                         │
│                                                              │
│  Estimated Total: $300 - $800 (depending on selections)     │
│                                                              │
│  [💬 Ask about specific items] [📋 Save bundle]            │
└────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority

### High Priority (MVP)

1. ✅ Basic bundle identification (LLM)
2. ✅ Product search per item
3. ✅ Grouping by priority
4. ✅ Frontend display with cards

### Medium Priority (V1.1)

5. Budget filtering
6. User level detection
7. Quantity suggestions
8. Better error handling

### Low Priority (V2.0)

9. Bundle templates
10. Smart substitutions
11. Bundle discounts
12. Comparison mode

---

Ready to implement! Start with the high-priority features and iterate based on user feedback. 🚀
