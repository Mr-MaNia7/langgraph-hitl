# AI Agent with HITL (Human in the loop)

This project implements an AI agent that can help with various tasks. The agent uses LangGraph for workflow management and OpenAI's GPT model for natural language understanding.

## Features

- Task analysis and planning
- Email sending capabilities
- Interactive conversation interface
- Web and CLI interfaces
- Action logging and monitoring

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- LangSmith API key (Optional - for tracking and logging)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Mr-MaNia7/langgraph-hitl.git
cd langgraph-hitl
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### Web Interface

1. Start the web server:

```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to `http://localhost:8000`

### CLI Interface

Run the CLI interface:

```bash
python cli.py
```

## Example Commands

1. Send an email:

```
Send an email to john@example.com reminding him about the meeting tomorrow
```

2. Create a document:

```
Create a document summarizing our project progress
```

3. Schedule a meeting:

```
Schedule a meeting with the team for next Monday at 2 PM
```

## Project Structure

- `chatagent.py`: Core agent implementation
- `main.py`: FastAPI web server
- `cli.py`: Command-line interface
- `frontend/`: React frontend application
- `requirements.txt`: Python dependencies

## Development

### Adding New Features

1. Define new action types in the `execute_action` function
2. Update the task analysis prompt in `analyze_task` if needed
3. Add any new environment variables to the `.env` file
