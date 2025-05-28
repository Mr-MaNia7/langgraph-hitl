from fastapi import FastAPI
from chatagent import graph_with_menu
from langgraph.types import Command
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "Welcome to your FastAPI backend!"}

@app.get("/chat_initiate")
def read_item(thread_id: str, response: str = None):
    thread_config = {"configurable": {"thread_id": thread_id}}    
    state = graph_with_menu.invoke(
        {"messages": [],
         "order": [],
         "finished": False}, 
        config=thread_config)

    return {
        "AIMessage": state["messages"][-1].content,
        "state": state
    }

@app.get("/chat-continue")
def continue_chat(thread_id: str, response: str):
    thread_config = {"configurable": {"thread_id": thread_id}}
    state = graph_with_menu.invoke(
        Command(resume = response), 
        config=thread_config)

    return {
        "AIMessage": state["messages"][-1].content,
        "state": state,
        "thread_id": thread_id
    }