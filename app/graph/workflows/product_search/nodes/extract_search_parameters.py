from typing import cast
from app.graph.workflows.product_search.types import ProductSearchState
from langchain_core.prompts import ChatPromptTemplate
from app.models.classifier import Entities
from app.services.llm import llm_service
from app.utils.conversation_context import format_conversation_context_with_template
async def extract_search_parameters_node(state: ProductSearchState) -> ProductSearchState:
    """
    LangGraph node for extracting parameters from the user query.
    Uses workflow-specific state management with conversation context.
    """
    # Get user message and format conversation context using the utility
    user_message = state.get("search_query", "")
    conversation_context = format_conversation_context_with_template(
        state=dict(state),  # Convert TypedDict to regular dict for type compatibility
        template_name="parameter_extraction",
        limit=5,
        fallback_message=""
    )
    
    extractor_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a parameter extractor for an e-commerce system. Extract parameters from user queries about products.

            For product_category, use these EXACT DummyJSON categories:
            - beauty (makeup, cosmetics)
            - fragrances (perfumes, scents)
            - furniture (beds, chairs, tables, sofas)
            - groceries (food items, beverages)
            - home-decoration (decor items, lighting, plant pots)
            - smartphones (mobile phones)
            - laptops (computers)
            - tablets (tablet devices)
            - mens-shirts (men's shirts)
            - womens-dresses (women's dresses)
            - womens-shoes (women's footwear)
            - mens-shoes (men's footwear or men's shoes)
            - womens-watches (women's watches)
            - mens-watches (men's watches)
            - womens-bags (women's bags, purses)
            - womens-jewellery (women's jewelry)
            - mens-jewellery (men's jewelry)
            - sunglasses (eyewear)
            - automotive (vehicles)
            - motorcycle (motorcycles)
            - lighting (lamps, lights)
            - sports-accessories (sports equipment)
            - kitchen-accessories (kitchen tools)
            - mobile-accessories (phone accessories)
            - skincare (skincare products)
            - tops (clothing tops)
            - vehicle (cars, trucks)

            Extract all relevant parameters including:
            - product_category (use EXACT categories above, not simplified ones)
            - brand
            - title (product name/title - use this ONLY for specific product names, not general terms)
            - tags (array of search tags that match user intent - this is the PRIMARY search mechanism)
            - gender (male, female, unisex)
            - price_max
            - price_min
            - size
            - rating_min (if user mentions rating requirements like "4+ stars", "highly rated")
            - stock_min (if user mentions availability like "in stock", "available")
            - availability_status ("In Stock", "Low Stock", "Out of Stock")

            IMPORTANT: Tags are the primary search mechanism. Extract relevant tags based on user query:

            Tag mapping examples (user query → tags to extract):
            - "perfumes" → ["fragrances", "perfumes"]
            - "mascara" → ["beauty", "mascara"]
            - "eyeshadow" → ["beauty", "eyeshadow"]
            - "iPhone" → ["smartphones", "apple"]
            - "Samsung phone" → ["smartphones", "samsung galaxy"]
            - "laptop" → ["laptops"]
            - "furniture" → ["furniture"]
            - "bed" → ["furniture", "beds"]
            - "chair" → ["furniture", "chairs"]
            - "table" → ["furniture", "tables", "bedside tables"]
            - "sofa" → ["furniture", "sofas"]
            - "kitchen tools" → ["kitchen accessories"]
            - "dress" → ["womens-dresses", "dresses"]
            - "men's shirt" → ["mens-shirts", "shirts"]
            - "women's shoes" → ["womens-shoes", "shoes"]
            - "men's shoes" → ["mens-shoes", "shoes"]
            - "sports equipment" → ["sports-accessories"]
            - "car" → ["automotive", "vehicles", "sedans"]
            - "motorcycle" → ["motorcycle"]
            - "home decor" → ["home-decoration"]
            - "phone accessories" → ["mobile-accessories", "phone accessories"]
            - "tablet" → ["tablets"]
            - "skincare" → ["skincare"]
            - "lighting" → ["lighting"]
            - "sunglasses" → ["sunglasses"]
            - "jewelry" → ["womens-jewellery"]
            - "watch" → ["mens-watches", "womens-watches"]
            - "bag" → ["womens-bags"]
            - "food" → ["groceries"]
            - "vegetables" → ["groceries", "vegetables"]

            Category mapping examples:
            - "laptop", "computer" → laptops
            - "smartphone", "phone", "mobile" → smartphones
            - "tablet", "ipad" → tablets
            - "mascara", "lipstick", "makeup" → beauty
            - "perfume", "fragrance", "cologne" → fragrances
            - "skincare", "moisturizer", "cleanser" → skincare
            - "bed", "chair", "table", "sofa" → furniture
            - "home decor", "decoration" → home-decoration
            - "kitchen tools", "kitchen utensils" → kitchen-accessories
            - "lamp", "light" → lighting
            - "men's shirt", "shirt for men" → mens-shirts
            - "women's dress", "dress for women" → womens-dresses
            - "women's shoes", "ladies shoes" → womens-shoes
            - "men's shoes", "men's footwear" → mens-shoes
            - "women's watch", "ladies watch" → womens-watches
            - "men's watch", "men's timepiece" → mens-watches
            - "women's bag", "purse", "handbag" → womens-bags
            - "women's jewelry", "ladies jewelry" → womens-jewellery
            - "sunglasses", "shades" → sunglasses
            - "car", "automobile" → automotive or vehicle
            - "motorcycle", "bike" → motorcycle
            - "sports equipment", "fitness gear" → sports-accessories
            - "phone accessories", "mobile accessories" → mobile-accessories
            - "clothing tops", "shirts", "blouses" → tops
            - "food", "snacks", "beverages" → groceries

            For brand and title always capitalize the first letter of the word.
            Example: "title": "Summer Breeze T-shirt", "brand": "Nike"

            Gender extraction:
            - "men's", "for men", "male" → gender: "male"
            - "women's", "for women", "female", "ladies" → gender: "female"
            - If not specified or unisex → gender: "unisex"

            Rating extraction:
            - "highly rated", "good reviews" → rating_min: 4.0
            - "5 star", "excellent" → rating_min: 5.0
            - "4+ stars" → rating_min: 4.0

            Stock/Availability extraction:
            - "in stock", "available" → availability_status: "In Stock"
            - "low stock" → availability_status: "Low Stock"
            - "out of stock" → availability_status: "Out of Stock"

            CRITICAL: 
            - Use 'title' only for specific product names (e.g., "iPhone 13 Pro", "Samsung Galaxy S10")
            - Use 'tags' for general product types (e.g., "perfumes", "mascara", "laptops", "tshirts")
            - Always extract relevant tags that match the user's search intent
            - Tags should be lowercase and match the patterns found in the product database
            - Make sure to fix any typos in the tags for example "tshirts" should be "t-shirts"

            If a parameter is not mentioned, set it to null."""),
        ("user", "{query}"),
        ("user", "{conversation_context}")
    ])

    llm = llm_service.get_llm_without_tools(disable_streaming=True)
    messages = extractor_prompt.invoke({"query": user_message, "conversation_context": conversation_context})
    response: Entities = cast(Entities, await llm.with_structured_output(Entities).ainvoke(messages))

    # Update workflow state with extracted parameters
    entities_dict = response.model_dump()
    
    
    state["search_query"] = user_message
    state["search_parameters"] = entities_dict
    state["search_results"] = []
    state["suggestions"] = []
    state["result_count"] = 0

    return state
