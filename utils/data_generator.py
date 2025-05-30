from langchain_openai import ChatOpenAI
import json
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class ProductDataGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

    def generate_products(self, num_products: int = 10) -> List[Dict[str, Any]]:
        """Generate sample product data using OpenAI."""
        prompt = f"""Generate {num_products} realistic product entries with the following fields:
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
        IMPORTANT: Do not include any text before or after the JSON array. Just the JSON array.
        """

        response = self.llm.invoke(prompt)
        
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
