import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from rich.syntax import Syntax
from typing import Optional, Any
import json
from config import LOG_FILE, LOG_LEVEL

# Create a custom theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red",
    "success": "green",
    "model": "blue",
    "user": "magenta",
    "action": "green",
    "system": "white"
})

# Initialize console with custom theme
console = Console(theme=custom_theme)

# Configure rich logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, console=console),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger("rich")

def log_model_message(content: str) -> None:
    """Log a message from the model with proper JSON formatting if applicable."""
    try:
        # Try to parse as JSON
        json_data = json.loads(content)
        
        # Format the JSON with indentation
        formatted_json = json.dumps(json_data, indent=2)
        
        # Create a syntax-highlighted version of the JSON
        syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=False)
        
        # Get the message type from JSON if available
        title = json_data.get("type", "Model").title()
        
        # Create a panel with the syntax-highlighted JSON
        console.print(Panel(
            syntax,
            title=title,
            border_style="blue"
        ))
        
    except json.JSONDecodeError:
        # If not JSON, display as regular text
        console.print(Panel(
            content,
            title="Model",
            border_style="blue"
        ))
    except Exception as e:
        # Handle any other errors gracefully
        console.print(Panel(
            f"[error]Error formatting model message:[/error]\n{str(e)}\n\n[info]Raw content:[/info]\n{content}",
            title="Model (Error)",
            border_style="red"
        ))

def log_user_input(content: str) -> None:
    """Log user input."""
    console.print(Panel(content, title="User", border_style="magenta"))

def log_action(action_type: str, description: str, outcome: str) -> None:
    """Log an action and its outcome."""
    console.print(Panel(
        f"[action]Action:[/action] {description}\n"
        f"[action]Type:[/action] {action_type}\n"
        f"[action]Outcome:[/action] {outcome}",
        title="Action",
        border_style="green"
    ))

def log_error(message: str, error: Optional[Exception] = None) -> None:
    """Log an error message."""
    if error:
        console.print(Panel(
            f"[error]{message}[/error]\n"
            f"[error]Error:[/error] {str(error)}",
            title="Error",
            border_style="red"
        ))
    else:
        console.print(Panel(
            f"[error]{message}[/error]",
            title="Error",
            border_style="red"
        ))

def log_success(message: str) -> None:
    """Log a success message."""
    console.print(Panel(
        f"[success]{message}[/success]",
        title="Success",
        border_style="green"
    ))

def log_info(message: str) -> None:
    """Log an info message."""
    console.print(Panel(
        f"[info]{message}[/info]",
        title="Info",
        border_style="cyan"
    ))

def log_warning(message: str) -> None:
    """Log a warning message."""
    console.print(Panel(
        f"[warning]{message}[/warning]",
        title="Warning",
        border_style="yellow"
    ))

def log_system(message: str) -> None:
    """Log a system message."""
    console.print(Panel(
        f"[system]{message}[/system]",
        title="System",
        border_style="white"
    ))
