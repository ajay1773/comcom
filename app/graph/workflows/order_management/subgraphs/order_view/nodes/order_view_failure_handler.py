from app.graph.workflows.order_management.types import OrderViewState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from app.services.widget_events import emit_order_view_failure
from app.services.llm import llm_service

async def order_view_failure_handler_node(state: OrderViewState, config: RunnableConfig | None = None) -> OrderViewState:
    """Handle failures in the order view workflow."""
    
    try:
        error_message = state.get("error_message", "An unknown error occurred")
        view_type = state.get("view_type", "unknown")
        
        print(f"Order view workflow failed: {error_message}")
        
        # Generate user-friendly error message using LLM
        error_context = {
            "error_message": error_message,
            "view_type": view_type,
            "is_auth_error": "authentication required" in error_message.lower() if error_message else False,
            "is_not_found": "not found" in error_message.lower() if error_message else False,
            "is_permission_error": "permission" in error_message.lower() if error_message else False,
            "is_invalid_request": "invalid" in error_message.lower() if error_message else False
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a helpful e-commerce assistant. Generate a friendly, empathetic error message for order viewing issues.
            
            Guidelines:
            - Be understanding and helpful
            - Use appropriate emojis to soften the message
            - Provide clear, actionable suggestions
            - Keep the tone supportive, not blaming the user
            - Be specific about what went wrong when possible
            - Offer alternative actions the user can take
            
            Error types to handle:
            - Authentication errors: User needs to sign in
            - Not found errors: Order doesn't exist or no orders found
            - Permission errors: User can't access this order
            - Invalid request errors: Request wasn't clear
            - General errors: Other technical issues
            """),
            ("user", """
            Error details:
            - Error message: {error_message}
            - View type: {view_type}
            - Is authentication error: {is_auth_error}
            - Is not found error: {is_not_found}
            - Is permission error: {is_permission_error}
            - Is invalid request: {is_invalid_request}
            
            Generate a helpful error message for the user.
            """)
        ])
        
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(prompt.invoke(error_context))
        
        user_message = str(response.content).strip()
        
        # Generate context-appropriate suggestions
        if error_context["is_auth_error"]:
            suggestions = ["Sign in to your account", "Create a new account"]
        elif error_context["is_not_found"]:
            if view_type == "single_order":
                suggestions = ["View all your orders", "Check order number spelling", "Browse products"]
            else:
                suggestions = ["Start shopping", "Browse products", "View product categories"]
        elif error_context["is_permission_error"]:
            suggestions = ["View your own orders", "Check if you're signed in to the correct account"]
        elif error_context["is_invalid_request"]:
            suggestions = [
                "Say 'show all my orders'",
                "Say 'show order 123'",
                "Say 'view my order history'"
            ]
        else:
            suggestions = [
                "Try again in a moment",
                "View all your orders",
                "Contact support if the problem persists"
            ]
        
        # Set the formatted response
        state["workflow_output_text"] = user_message

        
        # Update suggestions for the chat interface
        state["suggestions"] = suggestions
        
        # Emit failure widget event
        error_type = "authentication" if "authentication" in error_message.lower() else \
                     "not_found" if "not found" in error_message.lower() else \
                     "permission" if "permission" in error_message.lower() else \
                     "validation" if "invalid" in error_message.lower() else \
                     "unknown"
        
        emit_order_view_failure(
            message=user_message,
            view_type=view_type,
            error_type=error_type,
            suggested_actions=suggestions
        )
        
        print(f"Generated failure response for order view: {user_message}")
        
        return state
        
    except Exception as e:
        print(f"Error in order view failure handler: {e}")
        
        # Fallback error response
        fallback_message = "❌ Sorry, something went wrong while trying to view your orders."
        fallback_suggestions = ["Try again", "Contact support"]
        
        state["workflow_output_text"] = fallback_message
        state["suggestions"] = fallback_suggestions
        
        # Emit fallback failure widget event
        emit_order_view_failure(
            message=fallback_message,
            error_type="system_error",
            suggested_actions=fallback_suggestions
        )
        
        return state
