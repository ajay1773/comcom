from typing import cast
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from app.graph.workflows.order_management.types import AddToCartState
from app.services.chat_history_state import get_conversation_context_for_workflow

class ProductDetails(BaseModel):
    """Product details extracted from user prompt."""
    product_name: str  # Main field for extraction
    title: str | None = None
    brand: str
    size: str | None = None
    quantity: str = '1'
    color: str | None = None

async def extract_product_details_from_prompt_node(state: AddToCartState) -> AddToCartState:
    """
    LangGraph node for extracting product details from the user prompt.
    Enhanced with conversation history for better context awareness.
    """
    # Get workflow-specific state
    user_message = state.get("search_query", "")

    # Get conversation context for better product extraction
    conversation_context = get_conversation_context_for_workflow(state, limit=5)

    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for an e-commerce system.
        Extract product details from user's purchase request.

        TASK:
        Extract these EXACT fields:
        - product_name: The complete product name as mentioned (e.g., "Summer Breeze T-shirt", "Aliceblue Sweater")
        - title: Product title/name
        - brand: The brand name as mentioned (e.g., "Nike", "Mclaughlin-Castillo")
        - size: The size if mentioned (e.g., "M", "Large", "10", "XL") - null if not mentioned
        - quantity: The quantity mentioned (default: "1")
        - color: The color if mentioned (e.g., "Red", "Blue", "Green") - null if not mentioned

        EXAMPLES:
        Input: "I'd like to buy the Summer Breeze T-shirt by Nike in size M"
        Output: {{
            "product_name": "Summer Breeze T-shirt",
            "title": "Summer Breeze T-shirt",
            "brand": "Nike",
            "size": "M",
            "quantity": "1",
            "color": null
        }}

        Input: "I want to order 2 Aliceblue Sweaters by Mclaughlin-Castillo in Large"
        Output: {{
            "product_name": "Aliceblue Sweater",
            "title": "Aliceblue Sweater",
            "brand": "Mclaughlin-Castillo",
            "size": "Large",
            "quantity": "2",
            "color": null
        }}

        Input: "Add the Red Dress by Fashion Co to my cart"
        Output: {{
            "product_name": "Red Dress",
            "title": "Red Dress",
            "brand": "Fashion Co",
            "size": null,
            "quantity": "1",
            "color": null
        }}

        RULES:
        1. Extract EXACT names as they appear in the text
        2. Include the full product name with color if mentioned in the name
        3. Keep brand names exactly as written
        4. Extract size only if explicitly mentioned (L, XL, 10, Small, etc.)
        5. Extract quantity from numbers like "2", "three", etc. (default: "1")
        6. Extract color from product names or separate mentions (Red, Blue, etc.)
        6. Extract the product title/name
        7. Do not add or remove any words from the names
        8. If conversation context is available, consider user's previous preferences when extracting details
        """ ),
        ("assistant", "{conversation_context}"),
        ("user", "{query}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)

    response = await llm.with_structured_output(ProductDetails).ainvoke(extractor_prompt.invoke({"query": user_message, "conversation_context": conversation_context}))

    # Update workflow state with extracted parameters
    response = cast(ProductDetails, response)
    product_details = response.model_dump()
    
    
    
    state["product_details"] = product_details
    state["quantity"] = response.quantity
    state["size"] = response.size
    state["color"] = response.color
    return state
