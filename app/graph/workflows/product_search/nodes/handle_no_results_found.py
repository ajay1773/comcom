from typing import  cast
from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm import llm_service


async def handle_no_results_found_node(state: ProductSearchState) -> ProductSearchState:
    """Handle no results found."""
    search_query = state.get("search_query", "")
    template_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a part of a helpful chatbot assistant in an e-commerce system.
        You are supposed to handle the case where no products were found for the user’s search input.
        You need to respond to the user that nothing matched their search.
        Keep in mind these things while responding to the user:
        1. Politely informs the user that nothing matched their search.
        2. Do not use technical words like "query", "results", or "response".
        3. Suggests they try a different search term.
        4. Keep the response short and concise of one line only.
        """),
        ("user", "{search_query}"),
    ])

    messages = template_prompt.invoke({"search_query": search_query})
    response = await llm_service.get_llm_without_tools().ainvoke(messages)
    response = cast(str, response)

    state["suggestions"] = [response]
    state["workflow_widget_json"] = {
        "template": "product_search_results",
        "payload": []
    }

    return state