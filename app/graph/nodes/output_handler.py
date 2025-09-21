"""Node for handling standardized workflow outputs."""
from langchain_core.runnables import RunnableConfig
from app.models.chat import GlobalState
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from app.services.llm import llm_service
from app.services.chat_history_state import chat_history_state

class ResponseStructure(BaseModel):
    template: str
    payload: dict

async def output_handler_node(
    state: GlobalState,
    config: RunnableConfig | None = None,
) -> GlobalState:
    """
    A generic node that processes workflow outputs and prepares them for streaming.
    This node expects workflows to set workflow_output_text and workflow_output_json.
    """
    # Get the current workflow's outputs
    text_output = state.get("workflow_output_text")
    json_output = state.get("workflow_output_json")

    response_structure = ChatPromptTemplate.from_messages([
        ("system", """
        You are a text response generator for an e-commerce system.

        You will be given a valid JSON structure representing the response of different workflows.
        This JSON can have any depth and keys. Example templates include:
        - "initiate_payment"
        - "payment_status_details"
        - "order_details"
        - "product_search_results"

        Your task is to generate a friendly and engaging text response for the user, based on the JSON template type.

        Guidelines:
        - If JSON contains "template": "initiate_payment" → respond like: "Here's the payment form 💳 Please enter your payment details to continue."
        - If JSON contains "template": "payment_status_details" → respond like: "Your payment details are ready 📄 Please review the status carefully."
        - If JSON contains "template": "order_details" → respond like: "Your order has been placed successfully 🎉 You can track it anytime."
        - If JSON contains "template": "product_search_results" → respond like: "Here are some products matching your search 🔍 Feel free to explore your options."
        - If JSON contains "template": "send_login_form" → respond like: "Here is the login form 📝 Please enter your email address and password to continue."
        - If JSON contains "template": "login_with_credentials" → respond like: "Welcome back! 🎉 You're successfully signed in."
        - If JSON contains "template": "send_signup_form" → respond like: "Here is the signup form 📝 Please fill in your details to create an account."
        - If JSON contains "template": "signup_with_details" → respond like: "Welcome! 🎉 Your account has been created successfully."
        - If JSON is empty, null, or just {{}} / [] → respond like: "Sorry 😔 No product found or order could not be placed."

        Response Rules:
        - Always use the same language as the user’s input.
        - Keep responses between 10–50 words.
        - Responses must include at least one emoji.
        - Responses should be clear, easy to understand, and indicate that the UI is ready for user interaction.
        - Do not copy or mention values from the JSON.
        - Do not say “text response is ready.”
        - Do not add explanations or hallucinate information beyond the intent.
        """),
        ("user", "{json_output}")
    ])

    llm = llm_service.get_llm_without_tools()

    # If we have explicit text output, use it instead of generating new text
    if text_output:
        response = None  # Don't generate LLM response if we have explicit text
    else:
        response = await llm.ainvoke(response_structure.invoke({"json_output": json_output}))


    # Check for errors first
    workflow_error = state.get("workflow_error")
    if workflow_error:
        # If there's a workflow error, let the error handler deal with it
        from app.graph.nodes.error_handler import error_handler_node
        return await error_handler_node(state, config)

    if text_output is None and json_output is None:
        # If no output is set, this is likely an error condition
        # Create a standardized error object
        from app.graph.nodes.error_handler import create_workflow_error
        state["workflow_error"] = create_workflow_error(
            workflow_name=state.get("current_workflow", "unknown"),
            error_type="no_output",
            message="No workflow output available"
        )
        # Let error handler process this
        from app.graph.nodes.error_handler import error_handler_node
        return await error_handler_node(state, config)

    # Update the state with processed outputs
    # Prioritize text_output, then LLM response
    if text_output:
        state["response"] = text_output
    elif response:
        if hasattr(response, 'content'):
            if isinstance(response.content, str):
                state["response"] = response.content
            elif isinstance(response.content, list) and len(response.content) > 0:
                state["response"] = str(response.content[0])
            else:
                state["response"] = str(response.content)
        else:
            state["response"] = str(response)
    else:
        state["response"] = "I'm processing your request..."

    state["workflow_output_text"] = text_output
    state["workflow_output_json"] = json_output

    # Add the assistant's response to the conversation history
    current_conversation_history = state.get("conversation_history", [])
    if state.get("response"):
        updated_conversation_history = chat_history_state.conversation_manager.add_assistant_message(
            current_conversation_history, state["response"]
        )
        state["conversation_history"] = updated_conversation_history

    return state
