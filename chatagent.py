from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict, Literal, List, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages.ai import AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, interrupt
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
from utils.tools import (
    generate_products,
    create_google_sheet,
    export_sheet,
    AVAILABLE_TOOLS
)

# Set up logging
logging.basicConfig(
    filename='agent_actions.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)

class SubTask(TypedDict):
    """Represents a subtask in the analysis."""
    description: str
    complexity: str  # "simple", "moderate", "complex"
    dependencies: List[str]  # IDs of tasks this depends on
    estimated_time: str  # e.g., "5 minutes", "1 hour"

class TaskAnalysis(TypedDict):
    """Represents the analysis of a task."""
    main_goal: str
    subtasks: List[SubTask]
    potential_risks: List[str]
    required_resources: List[str]
    estimated_total_time: str

class Action(TypedDict):
    """Represents a single action in the plan."""
    action_type: str
    description: str
    parameters: Dict[str, str]
    status: str  # "pending", "completed", "failed"
    subtask_id: str  # Reference to the subtask this action fulfills

class Plan(TypedDict):
    """Represents a complete action plan."""
    goal: str
    analysis: TaskAnalysis
    actions: List[Action]
    status: str  # "draft", "confirmed", "executing", "completed", "cancelled"

class AgentState(TypedDict):
    """State representing the agent's conversation and actions."""
    messages: Annotated[list, add_messages]
    current_plan: Plan | None
    needs_confirmation: bool
    finished: bool
    tools_output: Dict[str, Any]  # Store tool outputs


def analyze_task(request: str) -> TaskAnalysis:
    """Analyze the task and determine if it needs to be broken down into subtasks using LLM."""
    prompt = f"""Analyze the following task and determine if it has the essential information needed to proceed.
    Task: {request}

    Essential information required for different task types:
    1. For email tasks (MUST have):
       - Recipient email address
       - Basic purpose or subject
    2. For product data tasks (MUST have):
       - Number of products
    3. For any task (MUST have):
       - Clear basic objective

    Optional information (nice to have but not required):
    - Detailed timeline
    - Complex dependencies

    If ANY essential information is missing, respond with:
    {{
        "needs_clarification": true,
        "clarification_questions": [
            "Specific question about missing essential information"
        ],
        "concerns": [
            "Specific concern about missing essential information"
        ]
    }}

    If ALL essential information is present (even if optional details are missing), provide a structured analysis including:
    1. Main goal
    2. Complexity assessment (simple/moderate/complex)
    3. List of subtasks (only if the task is complex) with:
       - Description
       - Estimated time
       - Dependencies (if any)
    4. Potential risks
    5. Required resources
    6. Total estimated time

    Format the response as a JSON object with the following structure:
    {{
        "main_goal": "string",
        "complexity": "simple|moderate|complex",
        "subtasks": [
            {{
                "description": "string",
                "estimated_time": "string",
                "dependencies": ["task_1", "task_2", ...]
            }}
        ],
        "potential_risks": ["string"],
        "required_resources": ["string"],
        "estimated_total_time": "string"
    }}

    Note: If the task is simple, the 'subtasks' array should be empty.
    IMPORTANT: Ensure the analysis is concise and only decomposes tasks when necessary.
    IMPORTANT: Your response MUST be a valid JSON object.
    IMPORTANT: Only ask for clarification if essential information is missing."""

    # Get analysis from LLM
    try:
        response = llm.invoke(prompt)
        # Extract JSON from the response
        content = response.content.strip()
        # Find the first { and last } to extract the JSON object
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")
        json_str = content[start:end]
        analysis = json.loads(json_str)
        
        # Check if we need clarification
        if "needs_clarification" in analysis and analysis["needs_clarification"]:
            # Ensure the clarification response has the required fields
            if not all(key in analysis for key in ["clarification_questions", "concerns"]):
                raise ValueError("Invalid clarification response structure")
            return analysis
        
        # Validate the structure for normal analysis
        if not all(key in analysis for key in ["main_goal", "complexity", "subtasks", "potential_risks", "required_resources", "estimated_total_time"]):
            raise ValueError("Invalid analysis structure")
        
        # Ensure subtasks have the required fields
        for subtask in analysis["subtasks"]:
            if not all(key in subtask for key in ["description", "estimated_time", "dependencies"]):
                raise ValueError("Invalid subtask structure")
        
        return analysis
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error parsing LLM response: {str(e)}")
        # Return a clarification request for the basic task
        return {
            "needs_clarification": True,
            "clarification_questions": [
                "What is the basic task you want to perform?",
                "What is the minimum information needed to start this task?"
            ],
            "concerns": [
                "The request is too vague to determine the basic task",
                "Unable to identify the essential requirements"
            ]
        }


def create_plan(request: str) -> Plan:
    """Create a detailed plan based on the user's request using LLM."""
    # First, analyze the task
    analysis = analyze_task(request)
    
    # If the analysis indicates we need clarification, return it directly
    if "needs_clarification" in analysis and analysis["needs_clarification"]:
        return {
            "goal": request,
            "analysis": analysis,
            "actions": [],
            "status": "needs_clarification"
        }
    
    # Generate actions based on the analysis using LLM
    prompt = f"""Based on the following task analysis, create a detailed action plan.
    Analysis: {json.dumps(analysis, indent=2)}

    For each subtask, create one or more specific actions that will accomplish it.
    Use the following action types where appropriate:
    - generate_products: For generating product data (requires num_products parameter)
    - create_sheet: For creating Google Sheets (requires title and data parameters)
    - export_sheet: For exporting Google Sheets (requires sheet_id and format (csv or xlsx) parameters)
    - send_email: For sending emails (requires recipient and subject parameters)
    - custom_action: For other types of actions

    Format the response as a JSON array of actions with the following structure:
    [
        {{
            "action_type": "string",
            "description": "string",
            "parameters": {{
                "key": "value"
            }},
            "status": "pending",
            "subtask_id": "task_X"
        }}
    ]

    Ensure the actions are specific, actionable, and aligned with the subtasks.
    IMPORTANT: Do not include any text before or after the JSON array. Just the JSON array."""

    # Get actions from LLM
    response = llm.invoke(prompt)
    
    try:
        # Parse the LLM response as JSON
        actions = json.loads(response.content)
        
        # Validate the structure of each action
        for action in actions:
            if not all(key in action for key in ["action_type", "description", "parameters", "status", "subtask_id"]):
                raise ValueError("Invalid action structure")
        
        return {
            "goal": request,
            "analysis": analysis,
            "actions": actions,
            "status": "draft"
        }
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Error parsing LLM response for actions: {str(e)}")
        raise e

def execute_action(action: Action, tools_output: Dict[str, Any] = None) -> str:
    """Execute a single action from the plan."""
    try:
        if action["action_type"] == "generate_products":
            num_products = int(action["parameters"].get("num_products", 3))
            # Use invoke() instead of direct call
            products = generate_products.invoke({"num_products": num_products})
            if tools_output is not None:
                tools_output["products"] = products
            return f"Generated {len(products)} products successfully"

        elif action["action_type"] == "create_sheet":
            if not tools_output or "products" not in tools_output:
                raise ValueError("No product data available. Generate products first.")
            
            title = action["parameters"].get("title", "Product List")
            # Use invoke() instead of direct call
            sheet_result = create_google_sheet.invoke({
                "title": title,
                "data": tools_output["products"]
            })
            if tools_output is not None:
                tools_output["sheet"] = sheet_result
            return f"Created Google Sheet: {sheet_result['shareable_link']}"

        elif action["action_type"] == "export_sheet":
            if not tools_output or "sheet" not in tools_output:
                raise ValueError("No sheet available. Create a sheet first.")
            
            format = action["parameters"].get("format", "csv")
            # Use invoke() instead of direct call
            export_path = export_sheet.invoke({
                "sheet_id": tools_output["sheet"]["sheet_id"],
                "format": format
            })
            if tools_output is not None:
                tools_output["export_path"] = export_path
            return f"Exported sheet to {export_path}"

        elif action["action_type"] == "send_email":
            # For now, just return a mock message since we're not implementing email
            return f"Email would be sent: {action['description']}"

        else:
            return f"Unknown action type: {action['action_type']}"

    except Exception as e:
        logging.error(f"Error executing action: {str(e)}")
        return f"Action failed: {str(e)}"

def log_action(action: Action, outcome: str) -> None:
    """Log the action and its outcome."""
    logging.info(f"Action: {action['description']} | Type: {action['action_type']} | Outcome: {outcome}")

def human_node(state: AgentState) -> AgentState:
    """Display the last model message to the user, and receive the user's input."""
    last_msg = state["messages"][-1]
    print("Model:", last_msg.content)

    user_input = interrupt("Give me your reply")
    print("User input:", user_input)

    if user_input.lower() in {"quit", "exit", "goodbye"}:
        return {
            "messages": [("user", user_input)],
            "current_plan": state.get("current_plan"),
            "needs_confirmation": state.get("needs_confirmation", False),
            "finished": True
        }

    return {
        "messages": [("user", user_input)],
        "current_plan": state.get("current_plan"),
        "needs_confirmation": state.get("needs_confirmation", False),
        "finished": False
    }

def maybe_exit_human_node(state: AgentState) -> Literal["planner", "agent", "__end__"]:
    """Route to the appropriate node based on the state."""
    if state.get("finished", False):
        return "__end__"
    
    # If we have a plan that needs confirmation, go to agent
    if state.get("current_plan") and state.get("needs_confirmation"):
        return "agent"
    
    # Otherwise, go to planner to create/modify the plan
    return "planner"

def format_clarification_request(analysis: dict) -> str:
    """Format the clarification request for display to the user."""
    output = {
        "type": "clarification_request",
        "title": "Task Needs Clarification",
        "concerns": analysis.get("concerns", []),
        "questions": analysis.get("clarification_questions", []),
        "suggestions": analysis.get("suggestions", [])
    }
    return json.dumps(output)

def format_plan_for_display(plan: Plan) -> str:
    """Format the plan for display to the user."""
    output = {
        "type": "plan",
        "title": "Task Analysis and Plan",
        "goal": plan["goal"],
        "analysis": {
            "complexity": plan["analysis"]["complexity"],
            "estimated_time": plan["analysis"]["estimated_total_time"],
            "subtasks": [
                {
                    "description": subtask["description"],
                    "estimated_time": subtask["estimated_time"],
                    "dependencies": subtask["dependencies"]
                }
                for subtask in plan["analysis"]["subtasks"]
            ],
            "risks": plan["analysis"]["potential_risks"],
            "resources": plan["analysis"]["required_resources"]
        },
        "actions": [
            {
                "description": action["description"],
                "type": action["action_type"],
                "status": action["status"],
                "parameters": action["parameters"]
            }
            for action in plan["actions"]
        ],
        "status": plan["status"]
    }
    return json.dumps(output)

def format_execution_results(plan: Plan, results: List[str]) -> str:
    """Format the execution results for display to the user."""
    output = {
        "type": "execution_results",
        "title": "Plan Execution Results",
        "status": plan["status"],
        "results": results,
        "summary": {
            "total_actions": len(plan["actions"]),
            "completed_actions": sum(1 for action in plan["actions"] if action["status"] == "completed"),
            "failed_actions": sum(1 for action in plan["actions"] if action["status"] == "failed")
        }
    }
    return json.dumps(output)

def format_error_message(error: str) -> str:
    """Format error messages consistently."""
    output = {
        "type": "error",
        "title": "Error Occurred",
        "message": error,
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(output)

def format_confirmation_request() -> str:
    """Format the confirmation request message."""
    output = {
        "type": "confirmation_request",
        "title": "Plan Confirmation Required",
        "message": "Please review and confirm if this plan looks correct.",
        "options": ["confirm", "modify", "cancel"]
    }
    return json.dumps(output)

def format_modification_request() -> str:
    """Format the modification request message."""
    output = {
        "type": "modification_request",
        "title": "Plan Modification",
        "message": "Please describe what changes you'd like to make to the plan.",
        "current_plan": "available"  # Indicates that the current plan is available for reference
    }
    return json.dumps(output)

# def create_tool_node() -> ToolNode:
#     """Create a ToolNode with our custom tools."""
#     return ToolNode(tools=AVAILABLE_TOOLS)

def planner_node(state: AgentState) -> AgentState:
    """The planner node that creates and modifies action plans."""
    if not state["messages"]:
        return {
            "messages": [AIMessage(content=json.dumps({
                "type": "greeting",
                "title": "Welcome",
                "message": "Hello! I can help you generate product data, create Google Sheets, and send emails. What would you like me to do?"
            }))],
            "current_plan": None,
            "needs_confirmation": False,
            "finished": False,
            "tools_output": {}
        }

    last_user_msg = state["messages"][-1]
    
    try:
        # If we have a plan and the user wants to modify it
        if state.get("current_plan") and "modify" in last_user_msg.content.lower():
            # Create a new plan based on the modification request
            new_plan = create_plan(last_user_msg.content)
            if new_plan["status"] == "needs_clarification":
                return {
                    "messages": [AIMessage(content=format_clarification_request(new_plan["analysis"]))],
                    "current_plan": None,
                    "needs_confirmation": False,
                    "finished": False,
                    "tools_output": {}
                }
            return {
                "messages": [AIMessage(content=format_plan_for_display(new_plan))],
                "current_plan": new_plan,
                "needs_confirmation": True,
                "finished": False,
                "tools_output": {}
            }
        
        # Create a new plan
        plan = create_plan(last_user_msg.content)
        
        # Check if we need clarification
        if plan["status"] == "needs_clarification":
            return {
                "messages": [AIMessage(content=format_clarification_request(plan["analysis"]))],
                "current_plan": None,
                "needs_confirmation": False,
                "finished": False,
                "tools_output": {}
            }
        
        # If no clarification needed, proceed with the plan
        return {
            "messages": [AIMessage(content=format_plan_for_display(plan))],
            "current_plan": plan,
            "needs_confirmation": True,
            "finished": False,
            "tools_output": {}
        }
    except Exception as e:
        logging.error(f"Error in planner node: {str(e)}")
        return {
            "messages": [AIMessage(content=format_error_message(str(e)))],
            "current_plan": None,
            "needs_confirmation": False,
            "finished": False,
            "tools_output": {}
        }

def agent_node(state: AgentState) -> AgentState:
    """The agent node that executes the confirmed plan."""
    if not state.get("current_plan"):
        return {
            "messages": [AIMessage(content=format_error_message("No plan to execute. Please create a plan first."))],
            "current_plan": None,
            "needs_confirmation": False,
            "finished": False,
            "tools_output": {}
        }

    last_user_msg = state["messages"][-1]
    
    if state.get("needs_confirmation"):
        # Check if user confirmed the plan
        if last_user_msg.content.lower() in {"yes", "confirm", "proceed"}:
            # Execute the plan
            plan = state["current_plan"]
            plan["status"] = "executing"
            results = []
            tools_output = {}
            
            for action in plan["actions"]:
                outcome = execute_action(action, tools_output)
                log_action(action, outcome)
                action["status"] = "completed"
                results.append(f"✓ {action['description']}: {outcome}")
            
            plan["status"] = "completed"
            return {
                "messages": [AIMessage(content=format_execution_results(plan, results))],
                "current_plan": plan,
                "needs_confirmation": False,
                "finished": False,
                "tools_output": tools_output
            }
        else:
            # User declined or wants modifications
            return {
                "messages": [AIMessage(content=format_modification_request())],
                "current_plan": state["current_plan"],
                "needs_confirmation": False,
                "finished": False,
                "tools_output": {}
            }
    
    return state

def maybe_route_to_tools(state: AgentState) -> Literal["planner", "agent", "human"]:
    """Route between different nodes based on the state."""
    if not state.get("messages", []):
        return "planner"
    
    if state.get("finished", False):
        return "human"
    
    return "human"

# Set up the graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("agent", agent_node)
graph_builder.add_node("human", human_node)
# graph_builder.add_node("tools", create_tool_node())

# Add edges
graph_builder.add_conditional_edges("planner", maybe_route_to_tools)
graph_builder.add_conditional_edges("agent", maybe_route_to_tools)
graph_builder.add_conditional_edges("human", maybe_exit_human_node)
graph_builder.add_edge(START, "planner")

# Compile the graph
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
