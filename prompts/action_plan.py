ACTION_PLAN_PROMPT = """Based on the following task analysis, create a detailed action plan.
Analysis: {analysis}

For each subtask, create one or more specific actions that will accomplish it.
Use the following action types where appropriate:
- generate_products: For generating product data (requires num_products parameter)
- create_sheet: For creating Google Sheets (requires title and data parameters)
- send_email: For sending emails (requires recipient and subject parameters. Optionally will include the shareable sheet link in the body)
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