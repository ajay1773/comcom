"""LLM node for identifying bundle items from use case."""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.services.llm import llm_service
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState


class BundleItemSchema(BaseModel):
    """Schema for LLM output."""
    category: str = Field(description="Product category (e.g., 'cricket bat', 'running shoes')")
    purpose: str = Field(description="What this item is used for")
    keywords: str = Field(description="Search keywords to find this product")
    priority: int = Field(description="1=essential, 2=recommended, 3=optional", ge=1, le=3)
    quantity: int = Field(description="Suggested quantity", ge=1)


class BundleAnalysis(BaseModel):
    """Complete bundle analysis from LLM."""
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

