-- Product Search Pipeline Database Indexes
-- Run this to create all necessary indexes for optimal search performance

-- Primary search indexes (MUST HAVE)
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products(category);

CREATE INDEX IF NOT EXISTS idx_products_brand
    ON products(brand);

CREATE INDEX IF NOT EXISTS idx_products_price
    ON products(price);

CREATE INDEX IF NOT EXISTS idx_products_rating
    ON products(rating DESC);

CREATE INDEX IF NOT EXISTS idx_products_stock
    ON products(stock DESC);

CREATE INDEX IF NOT EXISTS idx_products_availability
    ON products(availability_status);

CREATE INDEX IF NOT EXISTS idx_products_gender
    ON products(gender);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_products_category_price
    ON products(category, price);

CREATE INDEX IF NOT EXISTS idx_products_category_brand
    ON products(category, brand);

CREATE INDEX IF NOT EXISTS idx_products_category_rating
    ON products(category, rating DESC);

CREATE INDEX IF NOT EXISTS idx_products_brand_price
    ON products(brand, price);

-- Full-text search index (OPTIONAL - for Phase 2)
CREATE INDEX IF NOT EXISTS idx_products_title_lower
    ON products(LOWER(title));

-- Analyze tables for query optimization
ANALYZE products;

