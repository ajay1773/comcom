from app.models.chat import GlobalState
from app.services.llm import llm_service
from app.services.workflow_state import get_workflow_state, update_workflow_state
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

class ProductDetails(BaseModel):
    """Product details extracted from user prompt."""
    product_name: str
    brand: str

async def extract_product_details_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for extracting product details from the user prompt.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "place_order")
    user_message = state.get("user_message", "")

    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for an e-commerce system.
        Extract product details from user's purchase request.

        TASK:
        Extract these EXACT fields:
        - product_name: The complete product name as mentioned (e.g., "Summer Breeze T-shirt", "Aliceblue Sweater")
        - brand: The brand name as mentioned (e.g., "Nike", "Mclaughlin-Castillo")

        EXAMPLES:
        Input: "I'd like to buy the Summer Breeze T-shirt by Nike"
        Output: {{
            "product_name": "Summer Breeze T-shirt",
            "brand": "Nike"
        }}

        Input: "I want to order the Aliceblue Sweater by Mclaughlin-Castillo"
        Output: {{
            "product_name": "Aliceblue Sweater",
            "brand": "Mclaughlin-Castillo"
        }}

        RULES:
        1. Extract EXACT names as they appear in the text
        2. Include the full product name with color if mentioned
        3. Keep brand names exactly as written
        4. Do not add or remove any words from the names
        """),
        ("user", "{query}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)

    response = await llm.with_structured_output(ProductDetails).ainvoke(extractor_prompt.invoke({"query": user_message}))

    # Update workflow state with extracted parameters
    workflow_state = {
        "extracted_product_details": response.model_dump(),
        "query": user_message,
    }

    # Update the global state with workflow-specific state
    return update_workflow_state(state, "place_order", workflow_state)
