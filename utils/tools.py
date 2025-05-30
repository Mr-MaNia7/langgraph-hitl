from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
from .data_generator import ProductDataGenerator
from .sheets_manager import GoogleSheetsManager
from datetime import datetime
from config import GOOGLE_SERVICE_ACCOUNT_PATH, EXPORT_DIR

# Initialize the utility classes
data_generator = ProductDataGenerator()
sheets_manager = GoogleSheetsManager(GOOGLE_SERVICE_ACCOUNT_PATH)

@tool
def generate_products(num_products: int = 10) -> List[Dict[str, Any]]:
    """Generate sample product data using OpenAI.
    
    Args:
        num_products: Number of products to generate (default: 10)
    
    Returns:
        List of product dictionaries with fields like product_id, name, description, etc.
    """
    return data_generator.generate_products(num_products)

@tool
def create_google_sheet(title: str, data: List[Dict[str, Any]]) -> Dict[str, str]:
    """Create a new Google Sheet with the provided data.
    
    Args:
        title: Title of the Google Sheet
        data: List of dictionaries containing the data to add
    
    Returns:
        Dictionary containing sheet_id and shareable_link
    """
    sheet_id = sheets_manager.create_sheet(title)
    sheets_manager.add_data_to_sheet(sheet_id, data)
    shareable_link = sheets_manager.get_shareable_link(sheet_id)
    return {
        "sheet_id": sheet_id,
        "shareable_link": shareable_link
    }

@tool
def export_sheet(sheet_id: str, format: str = "csv") -> str:
    """Export a Google Sheet to a file.
    
    Args:
        sheet_id: ID of the Google Sheet to export
        format: Export format ("csv" or "xlsx")
    
    Returns:
        Path to the exported file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if format == "csv":
        output_path = f"{EXPORT_DIR}/products_{timestamp}.csv"
        return sheets_manager.export_as_csv(sheet_id, output_path)
    else:
        output_path = f"{EXPORT_DIR}/products_{timestamp}.xlsx"
        return sheets_manager.export_as_excel(sheet_id, output_path)

# List of all available tools
AVAILABLE_TOOLS = [
    generate_products,
    create_google_sheet,
    export_sheet
]
