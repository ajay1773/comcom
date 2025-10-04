from pydantic import BaseModel, Field
from typing import Literal


class Entities(BaseModel):
    """Entities model for product search parameters."""

    # EXACT DummyJSON categories
    product_category: (
        Literal[
            "beauty", "fragrances", "furniture", "groceries", "home-decoration",
            "smartphones", "laptops", "tablets", "mens-shirts", "womens-dresses",
            "womens-shoes", "mens-shoes", "womens-watches", "mens-watches",
            "womens-bags", "womens-jewellery", "sunglasses", "automotive",
            "motorcycle", "lighting", "sports-accessories", "kitchen-accessories",
            "mobile-accessories", "skincare", "tops", "vehicle"
        ] | None
    ) = Field(..., description="The exact DummyJSON category of the product")
    
    # Product identification
    brand: str | None = Field(..., description="The brand of the product")
    title: str | None = Field(..., description="The title/name of the product - use only for specific product names")
    tags: list[str] | None = Field(..., description="Array of search tags that match user intent - primary search mechanism")
    
    # Pricing
    price_max: float | None = Field(..., description="The maximum price of the product")
    price_min: float | None = Field(..., description="The minimum price of the product")
    
    # Product attributes
    gender: Literal["male", "female", "unisex"] | None = Field(..., description="The gender target of the product")
    size: str | None = Field(..., description="The size of the product")
    
    # DummyJSON specific fields
    rating_min: float | None = Field(..., description="Minimum rating filter (1-5 stars)")
    stock_min: int | None = Field(..., description="Minimum stock availability")
    availability_status: Literal["In Stock", "Low Stock", "Out of Stock"] | None = Field(
        ..., description="Product availability status"
    )
    


class Classifier(BaseModel):
    """Classifier model for intent classification and entity extraction."""

    intent: Literal[
        "product_search", "place_order", "initiate_payment", "payment_status",
        "support_query", "faq", "smalltalk", "unknown", "generate_signin_form",
        "login_with_credentials", "generate_signup_form", "signup_with_details",
        "add_to_cart", "view_cart", "delete_from_cart", "user_profile",
        "user_addresses", "add_address_form", "edit_address", "delete_address",
        "checkout", "checkout_ui_provider", "checkout_processor", "order_view"
    ] = Field(
        ..., description="The intent of the user query"
    )
    entities: Entities = Field(..., description="The extracted entities from the user query")
