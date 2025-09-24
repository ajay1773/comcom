from typing import cast
from langchain_core.prompts import ChatPromptTemplate
from app.graph.workflows.auth_middleware.types import AuthMiddlewareState
from app.services.llm import llm_service


async def handle_invalid_token_node(state: AuthMiddlewareState) -> AuthMiddlewareState:
    """
    Handle invalid token case by generating an appropriate error message 
    using LLM and stopping workflow execution.
    """
    
    llm = llm_service.get_llm_without_tools()
    auth_error = state.get("auth_error", "Authentication failed")
    target_workflow = state.get("target_workflow", "requested action")
    
    # Create prompt template for auth error message
    auth_error_prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
        You are an e-commerce chatbot. Generate a short, friendly message that:
        1. Politely informs the user that they need to be logged in.
        2. Does not use technical words like 'token', 'authentication', 'authorization', or 'JWT'
        3. Keeps the tone conversational and natural, as if chatting with a human
        4. Add the feature details which is envoked by the user in the message.
          For example if the user wants to access product search, then add the product search details in the message.
        
        Output must be a single friendly sentence, nothing else.
        """),
        ("user", "User tried to access {target_workflow} but authentication failed: {error}")
    ])
    
    # Generate error message using LLM
    error_message = await llm.ainvoke(
        auth_error_prompt_template.invoke({
            "target_workflow": target_workflow,
            "error": auth_error
        })
    )
    
    # Update state with error information
    state["suggestions"] = [cast(str, error_message)]
    # state["workflow_widget_json"] = {}
    
    return state
