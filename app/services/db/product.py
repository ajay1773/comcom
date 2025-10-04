
import json
from typing import Any, Dict, List, cast
from app.services.db.db import Product, db_service


class ProductService:

    def __init__(self):
        self.db_service = db_service

    def _convert_row_to_product(self, row) -> Product:
        """Convert database row to Product object."""
        tags = json.loads(row[8]) if row[8] else []
        dimensions = json.loads(row[12]) if row[12] else {}
        images = json.loads(row[19]) if row[19] else []
        available_sizes = json.loads(row[22]) if row[22] else []
        
        return cast(Product, {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "category": row[3],
            "price": row[4],
            "discount_percentage": row[5],
            "rating": row[6],
            "stock": row[7],
            "tags": json.dumps(tags),
            "brand": row[9],
            "sku": row[10],
            "weight": row[11],
            "dimensions": json.dumps(dimensions),
            "warranty_information": row[13],
            "shipping_information": row[14],
            "availability_status": row[15],
            "return_policy": row[16],
            "minimum_order_quantity": row[17],
            "thumbnail": row[18],
            "images": json.dumps(images),
            "barcode": row[20],
            "qr_code": row[21],
            "available_sizes": json.dumps(available_sizes),
            "unit": row[23],
            "gender": row[24],
        })

    async def get_products(self, product_details: Dict[str, Any]) -> List[Product]:
        """Get products from the database."""

        # Build query
        conditions = []
        params = []

        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])

        if product_details.get("gender"):
            conditions.append("gender = ?")
            params.append(product_details["gender"][0].upper())

        if product_details.get("price_max"):
            conditions.append("price <= ?")
            params.append(product_details["price_max"])

        if product_details.get("price_min"):
            conditions.append("price >= ?")
            params.append(product_details["price_min"])
        
        if product_details.get("brand"):
            conditions.append("brand LIKE ?")
            params.append(f"%{product_details['brand']}%")

        if product_details.get("title"):
            conditions.append("title LIKE ?")
            params.append(f"%{product_details['title']}%")
        
        # Tag-based search - primary search mechanism with specificity priority and normalization
        if product_details.get("tags"):
            tags = product_details["tags"]
            
            # Tag normalization mapping (user input -> database variations)
            tag_variations = {
                "chair": ["chairs", "chair"],
                "table": ["tables", "bedside tables", "table"],
                "bed": ["beds", "bed"],
                "sofa": ["sofas", "sofa"],
                "desk": ["desks", "desk"],
                "lamp": ["lamps", "lighting", "lamp"],
                "phone": ["smartphones", "phone accessories", "phone"],
                "laptop": ["laptops", "laptop"],
                "tablet": ["tablets", "tablet"],
                "perfume": ["fragrances", "perfumes", "perfume"],
                "mascara": ["mascara", "beauty"],
                "eyeshadow": ["eyeshadow", "beauty"],
                "shirt": ["shirts", "men's shirts", "shirt"],
                "dress": ["dresses", "girls' dresses", "dress"],
                "charger": ["chargers", "charger"],
                "case": ["phone accessories", "case"],
                "football": ["american football", "football"],
                "car": ["vehicles", "sedans", "car"],
            }
            
            # Normalize tags to include variations
            normalized_tags = []
            for tag in tags:
                if tag.lower() in tag_variations:
                    normalized_tags.extend(tag_variations[tag.lower()])
                else:
                    normalized_tags.append(tag)
            
            # Remove duplicates while preserving order
            normalized_tags = list(dict.fromkeys(normalized_tags))
            
            # Prioritize specific tags over general category tags
            general_categories = ["furniture", "electronics", "clothing", "beauty", "sports equipment", "home decor"]
            specific_tags = [tag for tag in normalized_tags if tag not in general_categories]
            general_tags = [tag for tag in normalized_tags if tag in general_categories]
            
            tag_conditions = []
            
            # If we have specific tags, prioritize them
            if specific_tags:
                for tag in specific_tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            # Only use general tags if no specific tags are available
            elif general_tags:
                for tag in general_tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            
            if tag_conditions:
                conditions.append("(" + " OR ".join(tag_conditions) + ")")

        query = "SELECT * FROM products"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Convert params list to tuple for proper parameter binding
        params_tuple = tuple(params) if params else None
        
        results = await db_service.execute_query(query, params_tuple)

        # Convert results into product objects
        products = cast(List[Product], [])
        if results:
            for row in results:
                products.append(self._convert_row_to_product(row))

        return products

    async def get_product(self, product_details: Dict[str, Any]) -> Product | None:
        """Get a single product from the database."""

        # Build query
        conditions = []
        params = []

        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])

        
        if product_details.get("title"):
            conditions.append("title = ?")
            params.append(product_details["title"])
        
        # Tag-based search for single product lookup with specificity priority and normalization
        if product_details.get("tags"):
            tags = product_details["tags"]
            
            # Tag normalization mapping (user input -> database variations)
            tag_variations = {
                "chair": ["chairs", "chair"],
                "table": ["tables", "bedside tables", "table"],
                "bed": ["beds", "bed"],
                "sofa": ["sofas", "sofa"],
                "desk": ["desks", "desk"],
                "lamp": ["lamps", "lighting", "lamp"],
                "phone": ["smartphones", "phone accessories", "phone"],
                "laptop": ["laptops", "laptop"],
                "tablet": ["tablets", "tablet"],
                "perfume": ["fragrances", "perfumes", "perfume"],
                "mascara": ["mascara", "beauty"],
                "eyeshadow": ["eyeshadow", "beauty"],
                "shirt": ["shirts", "men's shirts", "shirt"],
                "dress": ["dresses", "girls' dresses", "dress"],
                "charger": ["chargers", "charger"],
                "case": ["phone accessories", "case"],
                "football": ["american football", "football"],
                "car": ["vehicles", "sedans", "car"],
            }
            
            # Normalize tags to include variations
            normalized_tags = []
            for tag in tags:
                if tag.lower() in tag_variations:
                    normalized_tags.extend(tag_variations[tag.lower()])
                else:
                    normalized_tags.append(tag)
            
            # Remove duplicates while preserving order
            normalized_tags = list(dict.fromkeys(normalized_tags))
            
            # Prioritize specific tags over general category tags
            general_categories = ["furniture", "electronics", "clothing", "beauty", "sports equipment", "home decor"]
            specific_tags = [tag for tag in normalized_tags if tag not in general_categories]
            general_tags = [tag for tag in normalized_tags if tag in general_categories]
            
            tag_conditions = []
            
            # If we have specific tags, prioritize them
            if specific_tags:
                for tag in specific_tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            # Only use general tags if no specific tags are available
            elif general_tags:
                for tag in general_tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
            
            if tag_conditions:
                conditions.append("(" + " OR ".join(tag_conditions) + ")")

        if product_details.get("id"):
            conditions.append("id = ?")
            params.append(product_details["id"])

        if product_details.get("sku"):
            conditions.append("sku = ?")
            params.append(product_details["sku"])

        if product_details.get("gender"):
            conditions.append("gender = ?")
            params.append(product_details["gender"][0].upper())

        if product_details.get("price_max"):
            conditions.append("price <= ?")
            params.append(product_details["price_max"])

        if product_details.get("brand"):
            conditions.append("brand = ?")
            params.append(product_details["brand"])

        if product_details.get("price_min"):
            conditions.append("price >= ?")
            params.append(product_details["price_min"])

        query = "SELECT * FROM products"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " LIMIT 1"

        # Convert params list to tuple for proper parameter binding
        results = await db_service.execute_query(query, tuple(params) if params else None)

        # Convert results into product objects
        if results:
            return self._convert_row_to_product(results[0])
        
        return None

    async def get_product_by_id(self, product_id: int) -> Product | None:
        """Get a product by its ID."""
        return await self.get_product({"id": product_id})

    async def search_products(self, search_term: str, limit: int = 20) -> List[Product]:
        """Search products by title, description, brand, or tags."""
        query = """
        SELECT * FROM products 
        WHERE title LIKE ? 
           OR description LIKE ? 
           OR brand LIKE ? 
           OR tags LIKE ?
        LIMIT ?
        """
        
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern, limit)
        
        results = await db_service.execute_query(query, params)
        
        products = cast(List[Product], [])
        if results:
            for row in results:
                products.append(self._convert_row_to_product(row))
        
        return products


product_service = ProductService()