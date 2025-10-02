from app.graph.workflows.order_management.types import CheckoutState
from langchain_core.runnables import RunnableConfig
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate

async def checkout_router_node(state: CheckoutState, config: RunnableConfig | None = None) -> CheckoutState:
    """Route checkout requests to appropriate subgraph based on user intent."""
    
    try:
        user_message = state.get("user_message", "")
        
        # Determine if this is a UI data request or a submission
        routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a checkout router that determines user intent for e-commerce checkout.
                
                Analyze the user's message and determine if they want to:
                1. "ui_data" - Get checkout form data (show checkout options, prepare checkout, etc.)
                2. "process_submission" - Submit checkout details (complete checkout with specific details)
                
                UI_DATA requests include:
                - "I want to checkout", "show me checkout options", "prepare checkout"
                - "checkout my cart", "buy these items", "proceed to checkout"
                - "buy [specific product]" (direct purchase setup)
                
                PROCESS_SUBMISSION requests include:
                - Specific address and payment details provided
                - "Use address 1 and credit card 4532...", "COD with first address"
                - Any message containing specific checkout form submission data
                
                If unclear, default to "ui_data".
                
                Respond with just one word: either "ui_data" or "process_submission"
            """),
            ("user", "{user_message}"),
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(routing_prompt.invoke({"user_message": user_message}))
        
        route_decision = str(response.content).strip().lower()
        
        # Set routing decision in state
        state["checkout_route"] = route_decision
        
        print(f"Checkout routing decision: {route_decision}")
        
        return state
        
    except Exception as e:
        print(f"Error in checkout router: {e}")
        # Default to UI data if routing fails
        state["checkout_route"] = "ui_data"
        return state
