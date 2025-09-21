from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service


async def display_search_results_node(state: ProductSearchState) -> ProductSearchState:
    """Display the search results."""

    search_query = state.get("search_query", "")
    search_results = state.get("search_results", [])
    results_count = len(search_results)

    if results_count == 1:
        system_prompt = """
        You are a helpful assistant in an e-commerce system.
        You will be given a user’s search input and one matching product.
        Generate a short, friendly message that:
        1. Acknowledges that one product has been found.
        2. Casually points the user’s attention to the area where the product is shown in the UI.
        3. Keeps the tone conversational and natural.
        """
    else:
        system_prompt = """
        You are a helpful assistant in an e-commerce system.
        You will be given a user’s search input and a list of matching products.
        Generate a short, friendly message that:
        1. Acknowledges that several products have been found.
        2. Casually points the user’s attention to the area where products are shown in the UI.
        3. Keeps the tone conversational and natural, as if chatting with a human.
        """

    # Build the prompt
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{search_query}"),
        ("user", "{search_results}"),
    ])

    # Call LLM
    llm = llm_service.get_llm_without_tools()
    messages = template_prompt.invoke({"search_query": search_query, "search_results": search_results})
    response = await llm.ainvoke(messages)
    response = str(response.content) if hasattr(response, "content") else str(response)

    state["workflow_widget_json"] = {
        "template": "product_search_results",
        "payload": search_results
    }
    state["suggestions"] = [response]

    return state
