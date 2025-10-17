from pydantic import BaseModel, Field
from typing import Literal


class Entities(BaseModel):
    """
    Simplified Pydantic model for FTS5-based search parameter extraction.
    Used with .with_structured_output() for ONE-TIME LLM extraction.
    """

    # Main search keywords (used for FTS5 full-text search)
    keywords: str = Field(
        default="",
        description="Main search terms extracted from query (product type, brand, attributes). Example: 'red shoes', 'Nike running shoes', 'iPhone 14 Pro'"
    )

    # Price filters
    price_min: float | None = Field(
        default=None,
        description="Minimum price if mentioned",
        ge=0
    )
    price_max: float | None = Field(
        default=None,
        description="Maximum price if mentioned",
        ge=0
    )

    # Rating filter
    rating_min: float | None = Field(
        default=None,
        description="Minimum rating (0-5) if mentioned",
        ge=0,
        le=5
    )

    # Gender filter (simplified: M, F, or null)
    gender: Literal["M", "F"] | None = Field(
        default=None,
        description="Gender: 'M' for men/male, 'F' for women/female, null if unspecified"
    )

    # Optional brand list for filtering
    brands: list[str] = Field(
        default_factory=list,
        description="List of brand names if explicitly mentioned (e.g., ['Nike', 'Adidas'])"
    )

    # Optional category list
    categories: list[str] = Field(
        default_factory=list,
        description="List of categories if mentioned (e.g., ['shoes', 'laptops'])"
    )

    # Sort preference
    sort_by: Literal["relevance", "price_asc", "price_desc", "rating", "newest"] | None = Field(
        default="relevance",
        description="Sort preference: 'relevance' (default), 'price_asc' (cheapest first), 'price_desc' (expensive first), 'rating' (highest rated), 'newest'"
    )

    # Stock filter
    in_stock_only: bool = Field(
        default=True,
        description="Whether to show only in-stock items. Default true unless user explicitly asks for all products"
    )
    
    # NEW: Product attribute filters
    colors: list[str] = Field(
        default_factory=list,
        description="Product colors (e.g., ['red', 'blue', 'black'])"
    )
    
    materials: list[str] = Field(
        default_factory=list,
        description="Product materials (e.g., ['leather', 'cotton', 'polyester'])"
    )
    
    styles: list[str] = Field(
        default_factory=list,
        description="Product styles (e.g., ['casual', 'formal', 'athletic'])"
    )
    
    patterns: list[str] = Field(
        default_factory=list,
        description="Product patterns (e.g., ['striped', 'plaid', 'solid'])"
    )
    
    sizes: list[str] = Field(
        default_factory=list,
        description="Available sizes (e.g., ['M', 'L', 'XL'] or ['8', '9', '10'])"
    )
    
    # NEW: Discount filter
    min_discount: float | None = Field(
        default=None,
        description="Minimum discount percentage (0-100)",
        ge=0,
        le=100
    )
    


class Classifier(BaseModel):
    """Classifier model for intent classification and entity extraction."""

    intent: Literal[
        "product_search", "product_bundle_search", "place_order", "initiate_payment", "payment_status",
        "support_query", "faq", "smalltalk", "unknown", "generate_signin_form",
        "login_with_credentials", "generate_signup_form", "signup_with_details",
        "add_to_cart", "view_cart", "edit_cart", "delete_from_cart", "user_profile",
        "user_addresses", "add_address_form", "edit_address", "delete_address",
        "checkout", "checkout_ui_provider", "checkout_processor", "order_view", "product_comparison"
    ] = Field(
        ..., description="The intent of the user query"
    )
    entities: Entities = Field(..., description="The extracted entities from the user query")
