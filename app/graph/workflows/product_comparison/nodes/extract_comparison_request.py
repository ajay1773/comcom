"""Extract comparison request details from user query."""

from typing import Optional, cast
from pydantic import BaseModel
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.utils.conversation_context import format_conversation_context_with_template
from app.graph.workflows.product_comparison.types import ProductComparisonState


class ProductIdentifier(BaseModel):
    """Product identifier details."""
    name: str = ""
    brand: Optional[str] = None
    color: Optional[str] = None



class ComparisonRequest(BaseModel):
    """Extracted comparison request details."""
    product_identifiers: list[ProductIdentifier]  # [{"name": "iPhone 14", "brand": "Apple", "color": "Red"}, ...]
    comparison_criteria: list[str]  # ["price", "features", "performance"]
    specific_question: str | None = None  # "which is better for gaming?"


async def extract_comparison_request_node(state: ProductComparisonState) -> ProductComparisonState:
    """Extract products and criteria for comparison from user query."""
    user_message = state.get("search_query", "")
    
    # Get conversation context
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="parameter_extraction",
        limit=5,
        fallback_message=""
    )
    
    extraction_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        ###Role:
        You are a product comparison request analyzer for an e-commerce system.
        Extract the products to compare and what criteria to focus on.
        You must always produce a valid JSON that can be parsed into the ComparisonRequest schema.
        
        ###Task:
        Extract:
        - product_identifiers: List of products to compare with name and brand (if available)
        - comparison_criteria: What aspects to compare (price, features, specs, rating, etc.)
        - specific_question: Any specific question about the comparison
        
        ###Examples:
        Input: "Compare iPhone 14 Pro vs Samsung Galaxy S23"
        Output:
        ```json
         {{
            "product_identifiers": [
                {{"name": "iPhone 14 Pro", "brand": "Apple"}},
                {{"name": "Galaxy S23", "brand": "Samsung"}}
            ],
            "comparison_criteria": ["price", "features", "performance", "camera"],
            "specific_question": null
        }}
        ``` 

        ####Input: "Can you compare Black Whisk and Bamboo Spatula?"
        ####Output:
        ```json
        {{
            "product_identifiers": [
                {{"name": "Black Whisk", "brand": null}},
                {{"name": "Bamboo Spatula", "brand": null}}
            ],
            "comparison_criteria": ["price", "features", "rating"],
            "specific_question": null
        }}
        ```
        ####Input: "Can you try again with only 2 products?" - note that brand is null if not mentioned
        ####Output:
        ```json
        {{
            "product_identifiers": [
                {{"name": "Black Whisk", "brand": null}},
                {{"name": "Bamboo Spatula", "brand": null}}
            ],
            "comparison_criteria": ["price", "features", "rating"],
            "specific_question": null
        }}
        ```
        ####Output: Understand the chat context and try to extract the products and criteria for comparison
        
        ####Input: "Which laptop is better for video editing: MacBook Pro or Dell XPS?"
        #### Output:
        ```json
        {{
            "product_identifiers": [
                {{"name": "MacBook Pro", "brand": "Apple"}},
                {{"name": "XPS", "brand": "Dell"}}
            ],
            "comparison_criteria": ["performance", "display", "price"],
            "specific_question": "which is better for video editing"
        }}
        ```
        ####Input: "Show me differences between Nike Air Max and Adidas Ultraboost"
        ####Output:
        ```json
        {{
            "product_identifiers": [
                {{"name": "Air Max", "brand": "Nike"}},
                {{"name": "Ultraboost", "brand": "Adidas"}}
            ],
            "comparison_criteria": ["price", "comfort", "design", "durability"],
            "specific_question": null
        }}
        ```

        ####Input (context):
        AI: Showing products — ["Nike Air Shirt", "Puma Sports Shirt", "Adidas Classic Shirt"]
        User: "compare the last 2"

        ####Output:
        ```json
        {{
            "product_identifiers": [
                {{"name": "Sports Shirt", "brand": "Puma"}},
                {{"name": "Classic Shirt", "brand": "Adidas"}}
            ],
            "comparison_criteria": ["price", "features", "rating"],
            "specific_question": null
        }}
        ```
        ###Rules:
        - In the product identifiers, extract the product name and brand if explicitly mentioned otherwise null
        - Extract at least 2 products (maximum 5 products)
        - Infer brand from product name if not explicitly mentioned
        - Default criteria if not specified: ["price", "features", "rating", "specifications"]
        - Extract the core product name (e.g., "iPhone" from "Apple iPhone 14 Pro")
        - Consider conversation context for missing details
        - If the user asks to try again then make sure to extract the products and criteria for comparison from the chat context
        - If conversation context mentions previous products, consider them
        - If no products can be extracted, return empty arrays:
            ```json
            {{
                "product_identifiers": [],
                "comparison_criteria": [],
                "specific_question": null
            }}
            ```
        - Do not hallucinate or make up products or criteria
        ### Reference Resolution
        - If the user says things like:
        - "compare these"
        - "compare the last 2"
        - "compare them"
        - "compare the previous products"
        - Then refer to the most recent products mentioned or shown in the conversation context.
        - Extract the last 2 product names from that list and use them as `product_identifiers`.
        - If the conversation context does not contain any product list, set `product_identifiers` to an empty list.
        """),
        ("assistant", "{conversation_context}"),
        ("user", "{query}")
    ])
    
    try:
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = cast(ComparisonRequest, await llm.with_structured_output(ComparisonRequest).ainvoke(
            extraction_prompt.invoke({
                "query": user_message,
                "conversation_context": conversation_context
            })
        ))
        
        # Store extracted data in state
        state["product_identifiers"] = [dict(p) for p in response.product_identifiers]
        state["comparison_criteria"] = response.comparison_criteria or ["price", "features", "rating"]
        state["user_context"] = response.specific_question or ""
        
        print(f"Extracted {len(state['product_identifiers'])} products for comparison")
        
    except Exception as e:
        print(f"Error extracting comparison request: {e}")
        state["error_message"] = f"Failed to understand comparison request: {str(e)}"
        state["product_identifiers"] = []
    
    return state

