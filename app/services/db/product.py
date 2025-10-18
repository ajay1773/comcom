
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
            "material": row[25] if len(row) > 25 else None,
            "style": row[26] if len(row) > 26 else None,
            "pattern": row[27] if len(row) > 27 else None,
            "color": row[28] if len(row) > 28 else None,
        })

    async def get_products(self, product_details: Dict[str, Any]) -> List[Product]:
        """
        Main search method with relevance scoring and ranking.
        
        Uses different strategies based on search_type:
        - specific: Prioritize exact title matches
        - general: Prioritize category matches
        - hybrid: Balance between category and specific attributes
        """
        search_type = product_details.get("search_type", "general")
        
        if search_type == "specific":
            return await self._get_products_specific(product_details)
        else:
            return await self._get_products_general(product_details)

    async def _get_products_specific(self, product_details: Dict[str, Any]) -> List[Product]:
        """Specific search with title-focused scoring and strict matching"""
        
        title = product_details.get("title", "")
        category = product_details.get("product_category", "")
        tags = product_details.get("tags", [])
        tag = tags[0] if tags else ""
        brand = product_details.get("brand", "")
        
        # For specific searches, title is mandatory
        if not title:
            # Fallback to general search if no title provided
            return await self._get_products_general(product_details)
        
        # Build filter conditions
        filter_conditions = []
        filter_params = []
        
        # Mandatory: Title must match (this is a specific search)
        filter_conditions.append("LOWER(title) LIKE ?")
        filter_params.append(f"%{title.lower()}%")
        
        # Optional brand filter (helps narrow down specific products)
        if brand:
            filter_conditions.append("LOWER(brand) = LOWER(?)")
            filter_params.append(brand)
        
        # Optional category filter
        if category:
            filter_conditions.append("category = ?")
            filter_params.append(category)
        
        # Price filters
        if product_details.get("price_min"):
            filter_conditions.append("price >= ?")
            filter_params.append(product_details["price_min"])
        
        if product_details.get("price_max"):
            filter_conditions.append("price <= ?")
            filter_params.append(product_details["price_max"])
        
        # Rating filter
        if product_details.get("rating_min"):
            filter_conditions.append("rating >= ?")
            filter_params.append(product_details["rating_min"])
        
        # Gender filter
        if product_details.get("gender"):
            gender_code = product_details["gender"][0].upper()
            filter_conditions.append("(gender = ? OR gender = 'U')")
            filter_params.append(gender_code)
        
        # Availability filter
        if product_details.get("availability_status"):
            filter_conditions.append("availability_status = ?")
            filter_params.append(product_details["availability_status"])
        
        where_clause = "WHERE " + " AND ".join(filter_conditions)
        
        # Query with scoring - using subquery to filter by relevance score
        query = f"""
        SELECT * FROM (
            SELECT *,
                (CASE 
                    WHEN LOWER(title) = LOWER(?) THEN 100
                    WHEN LOWER(title) LIKE LOWER(?) || '%' THEN 80
                    WHEN LOWER(title) LIKE '%' || LOWER(?) || '%' THEN 60
                    ELSE 0
                END) * 0.5 +
                (CASE 
                    WHEN category = ? THEN 100
                    ELSE 0
                END) * 0.15 +
                (CASE 
                    WHEN LOWER(tags) LIKE '%' || LOWER(?) || '%' THEN 60
                    ELSE 0
                END) * 0.2 +
                (CASE 
                    WHEN LOWER(brand) = LOWER(?) THEN 100
                    ELSE 0
                END) * 0.05 +
                (CASE 
                    WHEN LOWER(description) LIKE '%' || LOWER(?) || '%' THEN 50
                    ELSE 0
                END) * 0.1
            AS relevance_score
            FROM products
            {where_clause}
        ) AS scored_products
        WHERE relevance_score >= 25
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 10
        """
        
        # Combine filter params + scoring params
        params = (
            *filter_params,       # WHERE clause filters
            title, title, title,  # Title scoring
            category or "",       # Category scoring
            tag,                  # Tag scoring
            brand or "",          # Brand scoring
            title,                # Description scoring
        )
        
        results = await db_service.execute_query(query, params)
        
        products = cast(List[Product], [])
        if results:
            for row in results:
                # Exclude the relevance_score column (last column)
                products.append(self._convert_row_to_product(row[:-1]))
        
        return products

    async def _get_products_general(self, product_details: Dict[str, Any]) -> List[Product]:
        """General/hybrid search with category-focused scoring"""
        
        category = product_details.get("product_category", "")
        tags = product_details.get("tags", [])
        tag = tags[0] if tags else ""
        title = product_details.get("title", "")
        brand = product_details.get("brand", "")
        
        # Build filter conditions
        filter_conditions = []
        filter_params = []
        
        if product_details.get("price_min"):
            filter_conditions.append("price >= ?")
            filter_params.append(product_details["price_min"])
        
        if product_details.get("price_max"):
            filter_conditions.append("price <= ?")
            filter_params.append(product_details["price_max"])
        
        if product_details.get("rating_min"):
            filter_conditions.append("rating >= ?")
            filter_params.append(product_details["rating_min"])
        
        if product_details.get("gender"):
            gender_code = product_details["gender"][0].upper()
            filter_conditions.append("(gender = ? OR gender = 'U')")
            filter_params.append(gender_code)
        
        if product_details.get("availability_status"):
            filter_conditions.append("availability_status = ?")
            filter_params.append(product_details["availability_status"])
        
        # Build WHERE clause
        where_clause = ""
        if category or tag or title or brand:
            conditions = ["("]
            score_params = []
            
            if category:
                conditions.append("category = ?")
                score_params.append(category)
            
            if tag:
                if len(conditions) > 1:
                    conditions.append(" OR LOWER(tags) LIKE ?")
                else:
                    conditions.append("LOWER(tags) LIKE ?")
                score_params.append(f"%{tag.lower()}%")
            
            if title:
                if len(conditions) > 1:
                    conditions.append(" OR LOWER(title) LIKE ?")
                else:
                    conditions.append("LOWER(title) LIKE ?")
                score_params.append(f"%{title.lower()}%")
            
            if brand:
                if len(conditions) > 1:
                    conditions.append(" OR LOWER(brand) LIKE ?")
                else:
                    conditions.append("LOWER(brand) LIKE ?")
                score_params.append(f"%{brand.lower()}%")
            
            conditions.append(")")
            where_clause = "WHERE " + "".join(conditions)
            filter_params = score_params + filter_params
        
        if filter_conditions:
            if where_clause:
                where_clause += " AND " + " AND ".join(filter_conditions)
            else:
                where_clause = "WHERE " + " AND ".join(filter_conditions)
        
        # Query with scoring (category-focused)
        query = f"""
        SELECT *,
            (CASE 
                WHEN category = ? THEN 100
                ELSE 0
            END) * 0.4 +
            (CASE 
                WHEN LOWER(tags) LIKE '%' || LOWER(?) || '%' THEN 80
                ELSE 0
            END) * 0.3 +
            (CASE 
                WHEN LOWER(title) LIKE '%' || LOWER(?) || '%' THEN 60
                ELSE 0
            END) * 0.2 +
            (CASE 
                WHEN LOWER(brand) = LOWER(?) THEN 100
                ELSE 0
            END) * 0.1
        AS relevance_score
        FROM products
        {where_clause}
        ORDER BY relevance_score DESC, rating DESC, stock DESC
        LIMIT 50
        """
        
        # Combine scoring params + filter params
        params = (
            category or "",  # Category scoring
            tag,             # Tag scoring
            title,           # Title scoring
            brand or "",     # Brand scoring
            *filter_params   # Additional filters
        )
        
        results = await db_service.execute_query(query, params)
        
        products = cast(List[Product], [])
        if results:
            for row in results:
                # Exclude the relevance_score column (last column)
                products.append(self._convert_row_to_product(row[:-1]))
        
        return products

    async def get_product(self, product_details: Dict[str, Any]) -> Product | None:
        """Get a single product from the database."""

        # Build query
        conditions = []
        params = []

        if product_details.get("product_category"):
            conditions.append("category = ?")
            params.append(product_details["product_category"])

        
        # Combined title and tag search for single product lookup
        search_conditions = []
        
        # Title search - case insensitive match for single product
        if product_details.get("title"):
            title = product_details["title"].lower()
            search_conditions.append("LOWER(title) LIKE ?")
            params.append(f"%{title}%")
        
        # Tag-based search - case insensitive approach
        if product_details.get("tags"):
            tags = product_details["tags"]
            
            for tag in tags:
                tag_lower = tag.lower()
                # Search in tags, title, and description with case insensitive matching
                search_conditions.append("(LOWER(tags) LIKE ? OR LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
                params.extend([f"%{tag_lower}%", f"%{tag_lower}%", f"%{tag_lower}%"])
        
        # Combine title and tag searches
        if search_conditions:
            conditions.append("(" + " OR ".join(search_conditions) + ")")

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

    def _sanitize_fts5_query(self, query: str) -> str:
        """
        Sanitize user input for FTS5 MATCH queries.
        Removes/escapes special FTS5 characters that could cause syntax errors.
        
        FTS5 special characters: " * ( ) AND OR NOT - (hyphen is NOT operator)
        Problem characters: & @ # $ % ^ ! ~ ` = + < > [ ] { } | backslash ; : , ?
        
        Args:
            query: Raw user search query
            
        Returns:
            Sanitized query safe for FTS5
        """
        import re
        
        if not query:
            return ""
        
        # Replace hyphens with spaces first (hyphens are FTS5 NOT operators)
        # This handles cases like "pull-up bar" -> "pull up bar"
        sanitized = query.replace('-', ' ')
        
        # Remove or replace other problematic characters
        # Keep: letters, numbers, spaces, apostrophes
        # Remove: &, @, #, $, %, ^, !, ~, `, =, +, <, >, [, ], {, }, |, \, ;, :, comma
        sanitized = re.sub(r'[&@#$%^!~`=+<>\[\]{}|\\;:,?]', ' ', sanitized)
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # If query is empty after sanitization, return original word tokens
        if not sanitized:
            # Extract just alphanumeric words from original query
            words = re.findall(r'\w+', query)
            sanitized = ' '.join(words)
        
        return sanitized

    async def search_products_fts(self, search_params: Dict[str, Any], limit: int = 20) -> List[Product]:
        """
        FTS5-based product search with filtering and sorting.
        This is the main search method for the FTS5 pipeline.
        
        Args:
            search_params: Dict containing:
                - keywords: str (required) - FTS5 search keywords
                - price_min: float (optional)
                - price_max: float (optional)
                - rating_min: float (optional)
                - gender: str (optional) - "M" or "F"
                - brands: list[str] (optional)
                - categories: list[str] (optional)
                - sort_by: str (optional) - "relevance", "price_asc", "price_desc", "rating", "newest"
                - in_stock_only: bool (optional, default True)
            limit: int - Maximum number of results
            
        Returns:
            List of Product objects ranked by relevance
        """
        keywords = search_params.get("keywords", "")
        
        # If no keywords, return empty results
        if not keywords or keywords.strip() == "":
            return []
        
        # Sanitize keywords for FTS5
        keywords = self._sanitize_fts5_query(keywords)
        
        # Build FTS5 query with JOIN to products table
        query = """
        SELECT
            p.*,
            fts.rank AS relevance_score
        FROM products_fts fts
        JOIN products p ON fts.product_id = p.id
        WHERE products_fts MATCH ?
        """
        
        query_params: List[Any] = [keywords]
        filters = []
        
        # Apply gender filter (include unisex 'U')
        if gender := search_params.get("gender"):
            filters.append("(p.gender = ? OR p.gender = 'U')")
            query_params.append(gender)
        
        # Apply price filters
        if price_min := search_params.get("price_min"):
            filters.append("p.price >= ?")
            query_params.append(price_min)
        
        if price_max := search_params.get("price_max"):
            filters.append("p.price <= ?")
            query_params.append(price_max)
        
        # Apply rating filter
        if rating_min := search_params.get("rating_min"):
            filters.append("p.rating >= ?")
            query_params.append(rating_min)
        
        # Apply brand filter (support multiple brands with OR)
        if brands := search_params.get("brands", []):
            if len(brands) > 0:
                brand_placeholders = " OR ".join(["LOWER(p.brand) = LOWER(?)"] * len(brands))
                filters.append(f"({brand_placeholders})")
                query_params.extend(brands)
        
        # Apply category filter (search in category field)
        if categories := search_params.get("categories", []):
            if len(categories) > 0:
                category_placeholders = " OR ".join(["LOWER(p.category) LIKE LOWER(?)"] * len(categories))
                filters.append(f"({category_placeholders})")
                query_params.extend([f"%{cat}%" for cat in categories])
        
        # Apply stock filter
        if search_params.get("in_stock_only", True):
            filters.append("p.stock > 0")
        
        # Apply color filter
        if colors := search_params.get("colors", []):
            if len(colors) > 0:
                color_placeholders = " OR ".join(["LOWER(p.color) LIKE LOWER(?)"] * len(colors))
                filters.append(f"({color_placeholders})")
                query_params.extend([f"%{color}%" for color in colors])
        
        # Apply material filter
        if materials := search_params.get("materials", []):
            if len(materials) > 0:
                material_placeholders = " OR ".join(["LOWER(p.material) LIKE LOWER(?)"] * len(materials))
                filters.append(f"({material_placeholders})")
                query_params.extend([f"%{mat}%" for mat in materials])
        
        # Apply style filter
        if styles := search_params.get("styles", []):
            if len(styles) > 0:
                style_placeholders = " OR ".join(["LOWER(p.style) LIKE LOWER(?)"] * len(styles))
                filters.append(f"({style_placeholders})")
                query_params.extend([f"%{style}%" for style in styles])
        
        # Apply pattern filter
        if patterns := search_params.get("patterns", []):
            if len(patterns) > 0:
                pattern_placeholders = " OR ".join(["LOWER(p.pattern) LIKE LOWER(?)"] * len(patterns))
                filters.append(f"({pattern_placeholders})")
                query_params.extend([f"%{pat}%" for pat in patterns])
        
        # Apply size filter
        if sizes := search_params.get("sizes", []):
            if len(sizes) > 0:
                # available_sizes is a JSON array, so we search within it
                size_placeholders = " OR ".join(["LOWER(p.available_sizes) LIKE LOWER(?)"] * len(sizes))
                filters.append(f"({size_placeholders})")
                query_params.extend([f'%"{size}"%' for size in sizes])
        
        # Apply discount filter
        if min_discount := search_params.get("min_discount"):
            filters.append("p.discount_percentage >= ?")
            query_params.append(min_discount)
        
        # Add all filters to query
        if filters:
            query += " AND " + " AND ".join(filters)
        
        # Apply sorting
        sort_by = search_params.get("sort_by", "relevance")
        if sort_by == "price_asc":
            query += " ORDER BY p.price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY p.price DESC"
        elif sort_by == "rating":
            query += " ORDER BY p.rating DESC, fts.rank DESC"
        elif sort_by == "newest":
            query += " ORDER BY p.id DESC"  # Assuming higher ID = newer
        else:  # relevance (default)
            query += " ORDER BY fts.rank DESC"
        
        # Add limit
        query += " LIMIT ?"
        query_params.append(limit)
        
        # Execute query
        results = await db_service.execute_query(query, tuple(query_params))
        
        # Convert results to Product objects
        products = cast(List[Product], [])
        if results:
            for row in results:
                # Note: row will have extra 'relevance_score' column, but we only need first 29 columns
                # (25 original + 4 new: material, style, pattern, color)
                product_row = row[:29]  # Get only product columns, skip relevance_score
                products.append(self._convert_row_to_product(product_row))
        
        return products


product_service = ProductService()