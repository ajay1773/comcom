from typing import cast
from pydantic import BaseModel
from app.graph.workflows.order_management.types import OrderViewState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service
from app.utils.conversation_context import format_conversation_context_with_template

class OrderViewParams(BaseModel):
    """Order view parameters extracted from user input."""
    view_type: str  # "all_orders" or "single_order"
    order_id: int | None = None
    order_number: str | None = None

async def extract_view_params_node(state: OrderViewState, config: RunnableConfig | None = None) -> OrderViewState:
    """Extract order view parameters from user's message."""
    
    user_message = state.get("search_query", "")
    
    # Get conversation context for better order extraction
    conversation_context = format_conversation_context_with_template(
        state=dict(state),
        template_name="order_processing",
        limit=5,
        fallback_message=""
    )
    
    try:
        # Create LLM prompt to extract order view parameters
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are an information extractor for order viewing requests.
                Extract the following details from the user's message:

                1. view_type: Determine if user wants to see "all_orders" or "single_order"
                2. order_id: Extract order ID if mentioned (numeric)
                3. order_number: Extract order number if mentioned (format: ORD-YYYYMMDD-XXXXXXXX)

                EXAMPLES:
                Input: "Show me all my orders"
                Output: {{"view_type": "all_orders", "order_id": null, "order_number": null}}

                Input: "View my order history"
                Output: {{"view_type": "all_orders", "order_id": null, "order_number": null}}

                Input: "Show me order 123"
                Output: {{"view_type": "single_order", "order_id": 123, "order_number": null}}

                Input: "I want to see order ORD-20240315-ABC12345"
                Output: {{"view_type": "single_order", "order_id": null, "order_number": "ORD-20240315-ABC12345"}}

                Input: "Check my order status for order ID 456"
                Output: {{"view_type": "single_order", "order_id": 456, "order_number": null}}

                RULES:
                - Default to "all_orders" if unclear
                - Extract numeric order IDs as integers
                - Extract order numbers exactly as mentioned
                - Use null for missing information
                - If conversation context is available, consider previous order interactions
            """),
            ("user", "{search_query}"),
            ("user", "{conversation_context}"),
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = cast(OrderViewParams, await llm.with_structured_output(OrderViewParams).ainvoke(
            prompt.invoke({"search_query": user_message, "conversation_context": conversation_context})
        ))
        
        # Set the extracted parameters in state
        state["view_type"] = response.view_type
        state["order_id"] = response.order_id
        state["order_number"] = response.order_number
        
        print(f"Extracted view params: Type={response.view_type}, ID={response.order_id}, Number={response.order_number}")
        
        return state
        
    except Exception as e:
        print(f"Error extracting view parameters: {e}")
        state["error_message"] = f"Failed to understand order view request: {str(e)}"
        state["view_success"] = False
        return state
