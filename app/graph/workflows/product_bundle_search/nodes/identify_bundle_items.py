"""LLM node for identifying bundle items from use case."""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict, Any, cast
from app.services.llm import llm_service
from app.graph.workflows.product_bundle_search.types import ProductBundleSearchState


class BundleItemSchema(BaseModel):
    """Schema for LLM output."""
    category: str = Field(description="Product category (e.g., 'sports-accessories', 'beauty', 'fragrances','furniture', 'home-decoration', 'smartphones', 'laptops', 'tablets', 'mens-shirts', 'mens-shoes', 'mens-watches', 'womens-dresses', 'womens-shoes', 'womens-watches', 'womens-bags', 'womens-jewellery', 'sunglasses', 'automotive', 'motorcycle', 'lighting', 'sports-accessories', 'kitchen-accessories', 'mobile-accessories', 'skincare', 'tops', 'vehicle')")
    purpose: str = Field(description="What this item is used for")
    keywords: str = Field(description="Search keywords to find this product (e.g., 'cricket bat', 'running shoes', 'tent', 'sleeping bag', 'flashlight', 'camping stove', 'backpack', 'dumbbells', 'yoga mat', 'resistance bands', 'jump rope', 'camera', 'tripod', 'memory card', 'camera bag', 'lens')")
    priority: int = Field(description="1=essential, 2=recommended, 3=optional", ge=1, le=3)
    quantity: int = Field(description="Suggested quantity", ge=1)


class BundleAnalysis(BaseModel):
    """Complete bundle analysis from LLM."""
    bundle_title: str = Field(description="Title for this bundle (e.g., 'Cricket Starter Kit')")
    bundle_description: str = Field(description="Brief description of the bundle")
    items: List[BundleItemSchema] = Field(description="List of products needed")


async def identify_bundle_items_node(state: ProductBundleSearchState) -> Dict[str, Any]:
    """
    Uses LLM to analyze the use case and identify required products.
    This is the intelligence layer that understands user needs.
    """

    user_query = state.get("search_query", "")
    use_case = state.get("use_case", user_query)
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
            3. **Use Clear Keywords**: Generate search terms that will find the right products
            4. **Be Realistic**: Suggest appropriate quantities

            Examples:
            - "I want to play cricket" → bat, ball, pads, gloves, helmet, shoes
            - "Going camping" → tent, sleeping bag, flashlight, camping stove, backpack
            - "Start home gym" → dumbbells, yoga mat, resistance bands, jump rope
            - "Photography hobby" → camera, tripod, memory card, camera bag, lens

            """),
                    ("user", """Use Case: {use_case}
            Budget: {budget}

            Identify all products needed for this use case. Return a comprehensive bundle.""")
    ])

    # Execute LLM call with structured output
    chain = prompt | llm_service.get_llm().with_structured_output(BundleAnalysis)

    result = cast(BundleAnalysis, await chain.ainvoke({
        "use_case": use_case,
        "budget": f"${budget}" if budget else "No budget specified"
    }))

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
        "bundle_description": result.bundle_description
    }

