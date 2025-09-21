

import json
from typing import Any, Dict, List, cast
from app.services.db.db import Product, db_service


class ProductService:

    def __init__(self):
        self.db_service = db_service

    async def get_products(self, product_details: Dict[str, Any]) -> List[Product]:
        """Get a product from the database."""

        # Build query
        conditions = []
        params = []

        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])

        if product_details .get("gender"):
            conditions.append("gender = ?")
            params.append(product_details["gender"][0].upper())

        if product_details.get("color"):
            conditions.append("color = ?")
            params.append(product_details["color"].capitalize())

        if product_details.get("price_max"):
            conditions.append("price <= ?")
            params.append(product_details["price_max"])

        if product_details.get("price_min"):
            conditions.append("price >= ?")
            params.append(product_details["price_min"])

        query = "SELECT * FROM products"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " LIMIT 10"

        results = await db_service.execute_query(query, params)

            # Convert results into product dicts
        products = cast(List[Product], [])
        if results:
            for row in results:
                images = json.loads(row[10]) if row[10] else []
                available_sizes = json.loads(row[11]) if row[11] else []
                products.append(cast(Product, {
                    "id": row[0],
                    "name": row[1],
                    "gender": row[4],
                    "category": row[2],
                    "min_price": row[3],
                    "max_price": row[3],
                    "color": row[9],
                    "brand": row[5],
                    "material": row[6],
                    "style": row[7],
                    "pattern": row[8],
                    "images": images,
                    "available_sizes": available_sizes,
                    "unit": row[12],
                }))

        return products



    async def get_product(self, product_details: Dict[str, Any]) -> Product | None:
        """Get a product from the database."""

        # Build query
        conditions = []
        params = []

        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])


        if product_details.get("name"):
            conditions.append("name = ?")
            params.append(product_details["name"])

        if product_details .get("gender"):
            conditions.append("gender = ?")
            params.append(product_details["gender"][0].upper())

        if product_details.get("color"):
            conditions.append("color = ?")
            params.append(product_details["color"].capitalize())

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
        query += " LIMIT 10"

        results = await db_service.execute_query(query, params)

            # Convert results into product dicts
        products = cast(List[Product], [])
        if results:
            for row in results:
                images = json.loads(row[10]) if row[10] else []
                available_sizes = json.loads(row[11]) if row[11] else []
                products.append(cast(Product, {
                    "id": row[0],
                    "name": row[1],
                    "gender": row[4],
                    "category": row[2],
                    "min_price": row[3],
                    "max_price": row[3],
                    "color": row[9],
                    "brand": row[5],
                    "material": row[6],
                    "style": row[7],
                    "pattern": row[8],
                    "images": images,
                    "available_sizes": available_sizes,
                    "unit": row[12],
                }))

        return products[0] if products else None


product_service = ProductService()