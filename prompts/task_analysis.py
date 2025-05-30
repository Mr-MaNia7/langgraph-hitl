TASK_ANALYSIS_PROMPT = """Analyze the following task and determine if it has the essential information needed to proceed.
Task: {request}

Essential information required for different task types:
1. For email tasks (MUST have):
   - Recipient email address
   - Basic purpose or subject
   - Optional: shareable sheet link
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