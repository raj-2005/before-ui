from typing import List
import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.graph.state import WorkflowState, Action

# -----------------------------------------
# LLM Setup
# -----------------------------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",   # fast + free tier friendly
    temperature=0
)

# -----------------------------------------
# Prompts
# -----------------------------------------

# 1. The Planner Prompt (Updated to handle chained scheduling/email)
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert workflow planner.
Convert the user's intent into a minimal list of executable workflow steps.

STRICT ALLOWED ACTIONS:
- "update_db": Use for saving, registering, or updating database records.
- "query_db": Use for searching or fetching data from the database.
- "write_file": Use for creating or writing to files.
- "send_email": Use for sending emails.
- "schedule_task": Use for scheduling tasks (requires "task_name" and "time" in params).

Return ONLY STRICT JSON in this format:
[
  {{
    "action": "write_file",
    "params": {{"path": "filename.txt", "content": ""}},
    "risk": "low"
  }}
]

Rules:
- Mark email actions as "medium" risk.
- If the user wants to schedule a task or set a reminder, you MUST create TWO steps: 
  1. "schedule_task" 
  2. "send_email" (to notify the owner).
- For "send_email", set "to" as "owner@example.com" unless otherwise specified.
- Do NOT use "insert_project" or "write_to_file". Use ONLY the STRICT ALLOWED ACTIONS.
- For "write_file", use the parameter name "path" for the filename.
- Do NOT include the "body" in params for email; the subtask node handles that.
- Do NOT include explanations.
"""),
    ("human", "{intent}"),
])

# 2. The Body Generation Prompt (UPDATED for Calendar Link acknowledgment)
BODY_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a professional email writer. 
Write a concise, professional email body.
Check the context: if 'scheduled_details' is present, you MUST write a confirmation email.
IMPORTANT: If 'scheduled_details' contains a Google Calendar URL (http...), include it clearly in the body so the user can click it.
Do NOT include the Subject line, Greeting (Hi...), or Sign-off (Sincerely...).
Just write the core message body text.
"""),
    ("human", "Intent: {intent}\nContext: {context}")
])

# 3. New Data/File Specialist Prompt
DATA_GEN_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
You are a Data Specialist. Your job is to format parameters for file and database operations.
Based on the user intent, provide the content to be written or the search query to be used.
Return ONLY the raw content/query text.
"""),
    ("human", "{intent}")
])

# -----------------------------------------
# Helper: Parse LLM JSON safely
# -----------------------------------------
def _parse_steps(json_text: str) -> List[Action]:
    """
    Cleans and parses JSON output from LLM.
    """
    try:
        # Remove markdown code blocks if present
        clean_text = re.sub(r'```json\s*|\s*```', '', json_text).strip()
        data = json.loads(clean_text)
        return [Action(**item) for item in data]
    except Exception as e:
        raise ValueError(f"Planner produced invalid JSON: {e}\nOutput: {json_text}")

# -----------------------------------------
# Node 1: Planner Node
# -----------------------------------------
def planner_node(state: WorkflowState) -> WorkflowState:
    """
    Creates the high-level execution plan.
    """
    if state.planned_steps:
        return state

    chain = PLANNER_PROMPT | llm
    response = chain.invoke({"intent": state.user_intent})
    
    # Debug print to see what LLM is doing
    print(f"DEBUG PLANNER RAW: {response.content}")

    steps = _parse_steps(response.content.strip())
    state.planned_steps = steps
    state.execution_logs.append(f"Planner created {len(steps)} steps.")
    
    return state

# -----------------------------------------
# Node 2: Body Generator Node
# -----------------------------------------
def body_generator_node(state: WorkflowState) -> WorkflowState:
    """
    If the current step is 'fetch_email_body', use AI to generate content.
    """
    if not state.planned_steps or state.current_step >= len(state.planned_steps):
        return state

    current_step_obj = state.planned_steps[state.current_step]
    
    if current_step_obj.action == "fetch_email_body" and "email_body" not in state.context:
        # Pass both intent and context so it sees 'scheduled_details'
        chain = BODY_GEN_PROMPT | llm
        response = chain.invoke({
            "intent": state.user_intent,
            "context": str(state.context)
        })
        
        state.context["email_body"] = response.content.strip()
        state.execution_logs.append("AI generated a custom email body based on intent.")
    
    return state

# New Node Function for handling file and db
def data_specialist_node(state: WorkflowState) -> WorkflowState:
    """
    Fills in content for file writing or search queries for DB lookups.
    """
    if not state.planned_steps or state.current_step >= len(state.planned_steps):
        return state

    step = state.planned_steps[state.current_step]
    
    if step.action in ["write_file", "query_db"] and not step.params.get("content") and not step.params.get("search_query"):
        chain = DATA_GEN_PROMPT | llm
        response = chain.invoke({"intent": state.user_intent})
        
        if step.action == "write_file":
            step.params["content"] = response.content.strip()
        else:
            step.params["search_query"] = response.content.strip()
            
        state.execution_logs.append(f"Data Specialist formatted parameters for {step.action}.")
    
    return state