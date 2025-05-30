PRODUCT_GENERATION_PROMPT = """Generate {num_products} realistic product entries with the following fields:
- product_id (unique string)
- name (string)
- description (string)
- price (float)
- category (string)
- stock_quantity (integer)
- rating (float between 1-5)
- created_at (ISO date string)

Return the data as a JSON array of objects. Make the data realistic and varied.
Include different categories like electronics, clothing, books, etc.
Ensure prices are realistic for each category.
IMPORTANT: Do not include any text before or after the JSON array. Just the JSON array.""" 