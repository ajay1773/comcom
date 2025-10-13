from typing import cast
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from app.graph.workflows.order_management.types import EditCartState
from app.services.chat_history_state import get_conversation_context_for_workflow


class EditDetails(BaseModel):
    """Edit details extracted from user prompt."""
    edit_type: str  # "remove", "update_quantity", "update_properties", "replace"
    target_product_reference: str  # How user refers to the item (e.g., "that shirt", "the red one")
    new_quantity: int | None = None  # For quantity updates
    new_size: str | None = None  # For property updates
    new_color: str | None = None  # For property updates
    replacement_product_name: str | None = None  # For replacements
    replacement_product_brand: str | None = None  # For replacements


async def extract_edit_details_node(state: EditCartState) -> EditCartState:
    """
    LangGraph node for extracting edit details from the user prompt.
    Enhanced with conversation history for better context awareness.
    
    This node understands context-aware references like:
    - "Remove that shirt"
    - "Change the size to large"
    - "Make it 3 instead of 2"
    - "Replace the red one with blue"
    """
    # Get workflow-specific state
    user_message = state.get("search_query", "")

    # Get conversation context for better understanding
    conversation_context = get_conversation_context_for_workflow(state, limit=10)

    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for cart edit operations in an e-commerce system.
        Extract cart edit details from user's request with context awareness.

        TASK:
        Extract these EXACT fields:
        - edit_type: The type of edit operation (MUST be one of: "remove", "update_quantity", "update_properties", "replace")
        - target_product_reference: How the user refers to the item they want to edit (e.g., "that shirt", "the red one", "the last item")
        - new_quantity: The new quantity if they want to update it (null otherwise)
        - new_size: The new size if they want to update it (null otherwise)
        - new_color: The new color if they want to update it (null otherwise)
        - replacement_product_name: Product name if they want to replace (null otherwise)
        - replacement_product_brand: Product brand if they want to replace (null otherwise)

        EDIT TYPE RULES:
        - "remove": User wants to delete an item (e.g., "remove that", "delete the shirt", "take out the red one")
        - "update_quantity": User wants to change quantity (e.g., "make it 3", "change to 2 pieces", "I want 5 instead")
        - "update_properties": User wants to change size/color/etc (e.g., "change size to large", "make it blue", "size XL instead")
        - "replace": User wants to swap one product for another (e.g., "replace with blue one", "change to different brand")

        CONTEXT AWARENESS:
        - Use conversation history to understand references like "that", "the one", "it", "the last one"
        - Identify what product the user is referring to from recent context
        - Extract the exact reference phrase used by the user

        EXAMPLES:

        Example 1:
        Conversation history:
        User: "Add Summer Breeze T-shirt by Nike to cart"
        Assistant: "Added Summer Breeze T-shirt to your cart"
        User: "Actually, remove that shirt"
        
        Output: {{
            "edit_type": "remove",
            "target_product_reference": "Summer Breeze T-shirt by Nike",
            "new_quantity": null,
            "new_size": null,
            "new_color": null,
            "replacement_product_name": null,
            "replacement_product_brand": null
        }}

        Example 2:
        Conversation history:
        User: "Add 2 Blue Jeans to cart"
        Assistant: "Added 2 Blue Jeans to your cart"
        User: "Make it 3 instead of 2"
        
        Output: {{
            "edit_type": "update_quantity",
            "target_product_reference": "Blue Jeans",
            "new_quantity": 3,
            "new_size": null,
            "new_color": null,
            "replacement_product_name": null,
            "replacement_product_brand": null
        }}

        Example 3:
        Conversation history:
        User: "Add Red Dress in size M to cart"
        Assistant: "Added Red Dress (M) to your cart"
        User: "Change that to size Large"
        
        Output: {{
            "edit_type": "update_properties",
            "target_product_reference": "Red Dress",
            "new_quantity": null,
            "new_size": "Large",
            "new_color": null,
            "replacement_product_name": null,
            "replacement_product_brand": null
        }}

        Example 4:
        Conversation history:
        User: "Add Blue Sweater by Nike to cart"
        Assistant: "Added Blue Sweater to your cart"
        User: "Actually, replace it with the Red Sweater by Adidas"
        
        Output: {{
            "edit_type": "replace",
            "target_product_reference": "Blue Sweater by Nike",
            "new_quantity": null,
            "new_size": null,
            "new_color": null,
            "replacement_product_name": "Red Sweater",
            "replacement_product_brand": "Adidas"
        }}

        IMPORTANT RULES:
        1. Always use conversation history to resolve references like "that", "it", "the one"
        2. Extract the actual product reference from context
        3. Be precise about edit_type classification
        4. Only fill fields relevant to the edit_type
        5. For replacements, extract both old and new product details
        6. Consider temporal references like "the last one I added"
        """ ),
        ("assistant", "Conversation History:\\n{conversation_context}"),
        ("user", "{query}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)

    response = await llm.with_structured_output(EditDetails).ainvoke(
        extractor_prompt.invoke({
            "query": user_message,
            "conversation_context": conversation_context
        })
    )

    # Update workflow state with extracted parameters
    response = cast(EditDetails, response)
    
    state["edit_type"] = response.edit_type
    state["target_product_reference"] = response.target_product_reference
    state["new_quantity"] = response.new_quantity
    state["new_size"] = response.new_size
    state["new_color"] = response.new_color
    
    # Store replacement product details if applicable
    if response.replacement_product_name or response.replacement_product_brand:
        state["replacement_product"] = {
            "name": response.replacement_product_name,
            "brand": response.replacement_product_brand
        }
    
    return state

