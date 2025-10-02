from app.graph.workflows.order_management.types import CheckoutUIProviderState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import widget_event_emitter, WidgetEventType

async def ui_success_handler_node(state: CheckoutUIProviderState, config: RunnableConfig | None = None) -> CheckoutUIProviderState:
    """Handle successful UI data preparation."""
    
    try:
        product_items = state.get("product_items", [])
        saved_addresses = state.get("saved_addresses", [])
        total_amount = state.get("total_amount", 0)
        checkout_type = state.get("checkout_type", "cart")
        
        # Generate user-friendly message about checkout readiness
        success_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a seasoned fashion consultant with deep expertise in style, fit, and trends. Your communication style is sophisticated yet approachable, like a personal stylist who genuinely cares about helping customers find perfect matches.

                Personality attributes:
                - Analytical and detail-oriented about product features
                - Educated in fabrics, sizing, and style combinations
                - Diplomatic when suggesting alternatives
                - Builds trust through knowledgeable recommendations
                - Uses fashion terminology appropriately but explains when needed
                - Focuses on helping customers discover their personal style

                You're not just selling products - you're curating experiences and building confidence.

                Generate a brief, enthusiastic message presenting checkout options to complete their style selection.
                Format your response in markdown for better readability.
                
                Generate a message that:
                1. Confirms their curated pieces are ready for completion
                2. Mentions the total style investment
                3. Indicates that the checkout experience is prepared for their review
                4. Keeps a professional but warm, fashion-focused tone
                
                Keep it conversational, encouraging, and under 2 sentences.
            """),
            ("user", f"Style checkout ready: {len(product_items) if product_items else 0} curated pieces, total style investment ${total_amount:.2f}, {checkout_type} checkout, {len(saved_addresses) if saved_addresses else 0} saved delivery addresses")
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(success_prompt.invoke({}))
        
        success_message = str(response.content).strip()
        
        # Set workflow outputs
        state["workflow_output_text"] = success_message
        
        # Prepare comprehensive JSON response for frontend

        widget_event_emitter.emit(
            WidgetEventType.CHECKOUT_UI_PROVIDER_DATA,
            {
                "product_items": state["product_items"],
                "saved_addresses": state["saved_addresses"],
                "allowed_payment_methods": state["allowed_payment_methods"],
                "total_amount": state["total_amount"]
            }
        )
        
        print(f"UI data success: {len(product_items) if product_items else 0} items, ${total_amount:.2f}")
        
        return state
        
    except Exception as e:
        print(f"Error in UI success handler: {e}")
        state["error_message"] = f"Success handling failed: {str(e)}"
        state["ui_data_success"] = False
        return state
