import json
from chatagent import graph
from langgraph.types import Command
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text
from datetime import datetime

console = Console()

def display_message(content: str) -> None:
    """Display a message with proper formatting based on its type."""
    try:
        message = json.loads(content)
        msg_type = message.get("type", "unknown")
        
        if msg_type == "greeting":
            console.print(Panel(
                Text(message["message"], style="bold green"),
                title=message["title"],
                border_style="green"
            ))
        
        elif msg_type == "clarification_request":
            table = Table(box=box.ROUNDED, show_header=False)
            table.add_column("Type", style="cyan")
            table.add_column("Content", style="white")
            
            if message.get("concerns"):
                table.add_row("⚠️ Concerns", "\n".join(f"• {c}" for c in message["concerns"]))
            
            if message.get("questions"):
                table.add_row("❓ Questions", "\n".join(f"{i+1}. {q}" for i, q in enumerate(message["questions"])))
            
            if message.get("suggestions"):
                table.add_row("💡 Suggestions", "\n".join(f"• {s}" for s in message["suggestions"]))
            
            console.print(Panel(
                table,
                title=message["title"],
                border_style="yellow"
            ))
        
        elif msg_type == "plan":
            table = Table(box=box.ROUNDED, show_header=False)
            table.add_column("Section", style="cyan")
            table.add_column("Content", style="white")
            
            # Goal
            table.add_row("🎯 Goal", message["goal"])
            
            # Analysis
            analysis = message["analysis"]
            table.add_row("📊 Analysis", 
                f"Complexity: {analysis['complexity']}\n"
                f"Estimated Time: {analysis['estimated_time']}"
            )
            
            # Subtasks
            if analysis["subtasks"]:
                subtasks_text = "\n".join(
                    f"{i+1}. {st['description']}\n"
                    f"   • Time: {st['estimated_time']}\n"
                    f"   • Dependencies: {', '.join(st['dependencies']) if st['dependencies'] else 'None'}"
                    for i, st in enumerate(analysis["subtasks"])
                )
                table.add_row("📝 Subtasks", subtasks_text)
            
            # Risks
            if analysis["risks"]:
                table.add_row("⚠️ Risks", "\n".join(f"• {r}" for r in analysis["risks"]))
            
            # Resources
            if analysis["resources"]:
                table.add_row("🔧 Resources", "\n".join(f"• {r}" for r in analysis["resources"]))
            
            # Actions
            actions_text = "\n".join(
                f"{i+1}. {a['description']}\n"
                f"   • Type: {a['type']}\n"
                f"   • Status: {a['status']}"
                for i, a in enumerate(message["actions"])
            )
            table.add_row("📋 Actions", actions_text)
            
            console.print(Panel(
                table,
                title=message["title"],
                border_style="blue"
            ))
        
        elif msg_type == "execution_results":
            table = Table(box=box.ROUNDED, show_header=False)
            table.add_column("Section", style="cyan")
            table.add_column("Content", style="white")
            
            # Results
            table.add_row("📊 Results", "\n".join(message["results"]))
            
            # Summary
            summary = message["summary"]
            table.add_row("📈 Summary", 
                f"Total Actions: {summary['total_actions']}\n"
                f"Completed: {summary['completed_actions']}\n"
                f"Failed: {summary['failed_actions']}"
            )
            
            console.print(Panel(
                table,
                title=message["title"],
                border_style="green"
            ))
        
        elif msg_type == "error":
            console.print(Panel(
                Text(message["message"], style="bold red"),
                title=message["title"],
                border_style="red"
            ))
        
        elif msg_type == "confirmation_request":
            console.print(Panel(
                Text(message["message"], style="bold yellow"),
                title=message["title"],
                border_style="yellow"
            ))
            console.print("\nOptions:", style="cyan")
            for option in message["options"]:
                console.print(f"• {option}", style="white")
        
        elif msg_type == "modification_request":
            console.print(Panel(
                Text(message["message"], style="bold yellow"),
                title=message["title"],
                border_style="yellow"
            ))
        
        else:
            # Fallback for unknown message types
            console.print(content)
    
    except json.JSONDecodeError:
        # Fallback for non-JSON messages
        console.print(content)

def main():
    """Main CLI loop."""
    console.print("[bold green]Welcome to the Agent CLI![/bold green]")
    console.print("Type 'quit' to exit.\n")
    
    # Initialize the graph with a unique thread ID
    thread_id = f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    thread_config = {"configurable": {"thread_id": thread_id}}
    
    # Initialize the graph
    state = graph.invoke(
        {"messages": [],
         "current_plan": None,
         "needs_confirmation": False,
         "finished": False},
        config=thread_config
    )
    
    # Display initial message
    if state["messages"]:
        display_message(state["messages"][-1].content)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in {"quit", "exit", "goodbye"}:
                console.print("\n[bold green]Goodbye![/bold green]")
                break
            
            # Process the input
            state = graph.invoke(
                Command(resume=user_input),
                config=thread_config
            )
            
            # Display the response
            if state["messages"]:
                display_message(state["messages"][-1].content)
            
            # Check if we're done
            if state.get("finished", False):
                break
        
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Exiting...[/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")

if __name__ == "__main__":
    main() 