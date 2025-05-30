import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

# Google Sheets Configuration
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")

# Logging Configuration
LOG_FILE = 'agent_actions.log'
LOG_FORMAT = '%(asctime)s - %(message)s'
LOG_LEVEL = 'INFO'

# Export Configuration
EXPORT_DIR = 'exports'
