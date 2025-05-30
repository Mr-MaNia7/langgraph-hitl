from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages

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
