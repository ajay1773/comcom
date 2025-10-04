//look for tables in the home category

SELECT * FROM products WHERE category = 'home' AND (tags LIKE '%tables%' OR tags LIKE '%bedside tables%' OR tags LIKE '%table%')