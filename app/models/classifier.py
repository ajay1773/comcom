from pydantic import BaseModel, Field
from typing import Optional
from typing_extensions import TypedDict, Annotated
from typing import Literal


class Entities(BaseModel):
    """Entities model."""

    gender: Literal["male", "female", "unisex"] | None = Field(
        ..., description="The gender of the user for the product"
    )
    product_category: (
        Literal["clothing", "shoes", "accessories", "bags", "jewelry", "other"] | None
    ) = Field(..., description="The category of the product")
    color: str | None = Field(..., description="The color of the product which is asked in question")
    price_max: float | None = Field(..., description="The maximum price of the product")
    price_min: float | None = Field(..., description="The minimum price of the product")
    size: str | None = Field(..., description="The size of the product which is asked in question")
    brand: str | None = Field(..., description="The brand of the product which is asked in question")
    material: str | None = Field(..., description="The material of the product which is asked in question")
    style: str | None = Field(..., description="The style of the product which is asked in question")
    pattern: str | None = Field(..., description="The pattern of the product which is asked in question")


class Classifier(BaseModel):
    """Classifier model."""

    intent: Literal["product_search", "order_status", "smalltalk", "other"] = Field(
        ..., description="The intent of the user query"
    )
    entities: Entities = Field(..., description="The entities of the user query")
