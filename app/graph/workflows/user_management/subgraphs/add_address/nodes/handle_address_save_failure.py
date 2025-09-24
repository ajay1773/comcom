"""Handle address save failure with LLM response."""

from app.graph.workflows.user_management.types import AddAddressState
from app.services.llm import llm_service
from langchain_core.prompts import ChatPromptTemplate


async def handle_address_save_failure_node(state: AddAddressState) -> AddAddressState:
    """Generate failure response for failed address save."""

    error_message = state.get("error_message", "Unknown error")
    extracted_address = state.get("extracted_address", {})
    
    # Create failure response prompt
    failure_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful e-commerce assistant handling an address save error.

        Generate a friendly, helpful error message for the user when their address couldn't be saved.

        Guidelines:
        - Acknowledge the issue apologetically but positively
        - Don't expose technical error details to the user
        - Suggest what the user can try next (like trying again or providing complete address)
        - Keep the tone supportive and solution-oriented
        - Keep response to 1-2 sentences maximum
        - Be conversational and reassuring

        Context:
        - User tried to save an address but it failed
        - We want to help them resolve the issue
        - Don't mention specific database or technical errors
        """),
        ("user", f"""Generate a helpful error message for this address save failure:
        
        Error: {error_message}
        Attempted Address: {extracted_address}
        
        Make it user-friendly and suggest next steps.
        """)
    ])

    try:
        # Generate failure message using LLM
        llm = llm_service.get_llm_without_tools(disable_streaming=True)
        response = await llm.ainvoke(failure_prompt.invoke({}))
        
        failure_message = str(response.content).strip()

    except Exception as e:
        print(f"Error generating failure message: {e}")
        # Fallback failure message based on error type
        if "missing" in error_message.lower() if error_message else False or "required" in error_message.lower() if error_message else False:
            failure_message = "I couldn't save your address because some required information is missing. Please provide your complete address including street, city, state, and ZIP code."
        elif "authentication" in error_message.lower() if error_message else False or "user not" in error_message.lower() if error_message else False:
            failure_message = "I couldn't save your address because you're not logged in. Please sign in first and try again."
        else:
            failure_message = "I'm sorry, I couldn't save your address right now. Please try again or contact support if the problem persists."

    # Set the failure response
    state["workflow_output_text"] = failure_message
    
    return state
