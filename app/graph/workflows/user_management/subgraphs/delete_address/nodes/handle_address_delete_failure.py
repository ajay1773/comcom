"""Handle address delete failure with LLM response."""

from app.graph.workflows.user_management.types import DeleteAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_address_delete_failure_node(state: DeleteAddressState) -> DeleteAddressState:
    """Generate failure response for failed address deletion."""

    error_message = state.get("error_message", "Unknown error") or "Unknown error"
    address_id = state.get("address_id")
    
    # Create failure response prompt
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling an address deletion error.

        Generate a friendly, helpful error message for the user when their address couldn't be deleted.

        Guidelines:
        - Acknowledge the issue apologetically but positively
        - Don't expose technical error details to the user
        - Suggest what the user can try next based on the error type
        - Keep the tone supportive and solution-oriented
        - Keep response to 1-2 sentences maximum
        - Be conversational and reassuring
        - For "only address" errors, explain they need at least one address
        - For "not found" errors, suggest checking the address ID
        - For authentication errors, suggest signing in

        Context:
        - User tried to delete an address but it failed
        - We want to help them resolve the issue
        - Don't mention specific database or technical errors
        """),
        ("user", f"""Generate a helpful error message for this address deletion failure:
        
        Error: {error_message}
        Address ID: {address_id}
        
        Make it user-friendly and suggest appropriate next steps based on the error type.
        """)
    ])

    try:
        # Generate failure message using LLM
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({"error_message": error_message, "address_id": address_id}))
        
        failure_message = str(response.content).strip()

    except Exception as e:
        print(f"Error generating failure message: {e}")
        # Fallback failure message based on error type
        if "not found" in error_message.lower():
            failure_message = f"I couldn't find address {address_id} in your account. Please check the address ID and try again."
        elif "only address" in error_message.lower():
            failure_message = "I can't delete your only address. Please add another address first, then you can delete this one."
        elif "authentication" in error_message.lower() or "user not" in error_message.lower():
            failure_message = "I couldn't delete your address because you're not logged in. Please sign in first and try again."
        elif "address id" in error_message.lower():
            failure_message = "Please specify which address you want to delete. For example, say 'Delete address 3' or 'Remove address ID 5'."
        else:
            failure_message = "I'm sorry, I couldn't delete your address right now. Please try again or contact support if the problem persists."

    # Set the failure response
    state["workflow_output_text"] = failure_message
    
    # Prepare JSON response for frontend
    state["workflow_output_json"] = {
        "success": False,
        "message": "Failed to delete address",
        "error": error_message,
        "address_id": address_id,
        "suggested_actions": [
            "View all addresses",
            "Check address ID" if "not found" in error_message.lower() else "Try again",
            "Add another address first" if "only address" in error_message.lower() else "Contact support if needed"
        ]
    }
    
    return state
