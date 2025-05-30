import json
from typing import List, Dict, Any
from llm import get_product_llm
from prompts.product_generation import PRODUCT_GENERATION_PROMPT

class ProductDataGenerator:
    def __init__(self):
        self.llm = get_product_llm()

    def generate_products(self, num_products: int = 10) -> List[Dict[str, Any]]:
        """Generate sample product data using OpenAI."""
        response = self.llm.invoke(PRODUCT_GENERATION_PROMPT.format(num_products=num_products))
        
        try:
            # Extract JSON from the response
            content = response.content.strip()
            start = content.find('[')
            end = content.rfind(']') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = content[start:end]
            products = json.loads(json_str)
            
            # Validate the structure
            required_fields = ['product_id', 'name', 'description', 'price', 
                             'category', 'stock_quantity', 'rating', 'created_at']
            
            for product in products:
                if not all(field in product for field in required_fields):
                    raise ValueError("Invalid product structure")
            
            return products
            
        except (json.JSONDecodeError, ValueError) as e:
            raise Exception(f"Error generating product data: {str(e)}") 
