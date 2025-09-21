from app.models.chat import GlobalState
from app.services.llm import llm_service
from app.models.classifier import Classifier
from langchain_core.prompts import ChatPromptTemplate
from app.services.workflow_state import get_workflow_state, update_workflow_state

class ExtractParamsNodes:
    def __init__(self):
        self.EXTRACT_PARAMS_NODE = "extract_params_node"

async def extract_params_node(state: GlobalState) -> GlobalState:
    """
    LangGraph node for extracting parameters from the user query.
    Uses workflow-specific state management.
    """
    # Get workflow-specific state
    workflow_state = get_workflow_state(state, "product_search")
    user_message = state.get("user_message", "")
    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for an e-commerce system. Extract parameters from user queries about products.

            For product_category, use these specific categories:
            - clothing (for shirts, t-shirts, pants, dresses, etc.)
            - shoes
            - accessories (for belts, scarves, hats, etc.)
            - bags
            - jewelry
            - other

            For gender, use:
            - male
            - female
            - unisex

            Extract all relevant parameters including:
            - gender
            - product_category
            - color
            - price_max
            - price_min
            - size
            - brand
            - material
            - style
            - pattern

            Be precise with categorization:
            - Shirts, t-shirts, pants, dresses go under "clothing"
            - Shoes, sneakers, boots go under "shoes"
            - Bags, purses go under "bags"
            - Jewelry includes necklaces, rings, earrings
            - Accessories includes belts, scarves, hats

            If a parameter is not mentioned, set it to null."""),
        ("user", "{query}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    messages = extractor_prompt.invoke({"query": user_message})
    response = await llm.with_structured_output(Classifier).ainvoke(messages)

    # Update workflow state with extracted parameters
    workflow_state = {
        "products": [],
        "filters": response.entities,
        "query": user_message,
        "response": ''
    }

    # Update the global state with workflow-specific state
    return update_workflow_state(state, "product_search", workflow_state)

