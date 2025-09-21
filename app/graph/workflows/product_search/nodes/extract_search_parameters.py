from typing import cast
from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate

from app.models.classifier import Classifier
from app.services.llm import llm_service


async def extract_search_parameters_node(state: ProductSearchState) -> ProductSearchState:
    """
    LangGraph node for extracting parameters from the user query.
    Uses workflow-specific state management.
    """
    # Get user message from search_query (passed from GlobalState via runner)
    user_message = state.get("search_query", "")
    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for an e-commerce system. Extract parameters from user queries about products.

            For product_category, use these specific categories:
            - clothing (for shirts, t-shirts, pants, dresses, etc.)
            - shoes
            - accessories (for belts, scarves, hats, etc.)
            - bags
            - jewelry
            - other

            For gender, use:
            - male
            - female
            - unisex

            Extract all relevant parameters including:
            - gender
            - product_category
            - color
            - price_max
            - price_min
            - size
            - brand
            - material
            - style
            - pattern

            Be precise with categorization:
            - Shirts, t-shirts, pants, dresses go under "clothing"
            - Shoes, sneakers, boots go under "shoes"
            - Bags, purses go under "bags"
            - Jewelry includes necklaces, rings, earrings
            - Accessories includes belts, scarves, hats

            For name, brand, material, style, pattern and color always capitalize the first letter of the word.
            Example: "name": "Summer Breeze T-shirt", "brand": "Nike", "material": "Cotton", "style": "Casual", "pattern": "Striped", "color": "Blue"

            If a parameter is not mentioned, set it to null."""),
        ("user", "{query}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    messages = extractor_prompt.invoke({"query": user_message})
    response: Classifier = cast(Classifier, await llm.with_structured_output(Classifier).ainvoke(messages))

    # Update workflow state with extracted parameters
    state["search_query"] = user_message
    state["search_parameters"] = response.entities.model_dump()
    state["search_results"] = []
    state["suggestions"] = []
    state["result_count"] = 0

    return state
