from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

# Initialize the main LLM for the chat agent
chat_llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)

# Initialize the LLM for product data generation
product_llm = ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)

def get_chat_llm() -> ChatOpenAI:
    """Get the main chat LLM instance."""
    return chat_llm

def get_product_llm() -> ChatOpenAI:
    """Get the product generation LLM instance."""
    return product_llm 
