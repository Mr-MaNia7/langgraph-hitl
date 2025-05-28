from fastapi import FastAPI
from chatagent import graph
from langgraph.types import Command
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, Literal

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Action(BaseModel):
    action_type: str
    description: str
    parameters: Dict[str, Any]
    status: str
    subtask_id: str

class SubTask(BaseModel):
    description: str
    estimated_time: str
    dependencies: List[str]

class TaskAnalysis(BaseModel):
    main_goal: str
    complexity: str
    subtasks: List[SubTask]
    potential_risks: List[str]
    required_resources: List[str]
    estimated_total_time: str

class Plan(BaseModel):
    goal: str
    analysis: TaskAnalysis
    actions: List[Action]
    status: str

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatResponse(BaseModel):
    messages: List[Message]
    needs_clarification: bool
    clarification_questions: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    current_plan: Optional[Plan] = None
    finished: bool = False

def format_state_for_response(state: Dict[str, Any]) -> ChatResponse:
    """Format the state into a standardized response."""
    messages = []
    for msg in state.get("messages", []):
        if isinstance(msg, tuple):
            role, content = msg
            messages.append(Message(role=role, content=content))
        elif hasattr(msg, 'content'):
            messages.append(Message(role="assistant", content=msg.content))
        elif isinstance(msg, dict):
            messages.append(Message(role=msg.get("role", "assistant"), content=msg.get("content", "")))

    needs_clarification = False
    clarification_questions = None
    concerns = None

    current_plan = state.get("current_plan")
    if current_plan and isinstance(current_plan, dict):
        if current_plan.get("status") == "needs_clarification":
            needs_clarification = True
            analysis = current_plan.get("analysis", {})
            clarification_questions = analysis.get("clarification_questions", [])
            concerns = analysis.get("concerns", [])

    return ChatResponse(
        messages=messages,
        needs_clarification=needs_clarification,
        clarification_questions=clarification_questions,
        concerns=concerns,
        current_plan=current_plan,
        finished=state.get("finished", False)
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Confirmation Agent API!"}

@app.get("/chat_initiate")
def start_chat(thread_id: str):
    """Start a new chat session."""
    thread_config = {"configurable": {"thread_id": thread_id}}    
    state = graph.invoke(
        {"messages": [],
         "current_plan": None,
         "needs_confirmation": False,
         "finished": False}, 
        config=thread_config)

    return format_state_for_response(state)

@app.get("/chat-continue")
def continue_chat(thread_id: str, response: str):
    """Continue an existing chat session."""
    thread_config = {"configurable": {"thread_id": thread_id}}
    state = graph.invoke(
        Command(resume=response), 
        config=thread_config)

    return format_state_for_response(state)
