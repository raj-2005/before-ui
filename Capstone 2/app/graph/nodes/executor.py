import os
from dotenv import load_dotenv

from app.graph.state import WorkflowState
from app.tools.email import send_email
from app.tools.file import read_file, write_file, query_database, write_to_db 
from app.tools.scheduler import schedule_task

# Load environment variables from .env
load_dotenv()


def executor_node(state: WorkflowState) -> WorkflowState:

    # Stop if already finished
    if state.finished:
        return state

    # Stop if no more steps
    if state.current_step >= len(state.planned_steps):
        state.finished = True
        return state

    step = state.planned_steps[state.current_step]
    action = step.action
    params = step.params # Helper for easier access

    try:
        step.status = "running"

        # =========================================
        # EMAIL ACTION
        # =========================================
        if action == "send_email":

            email_user = os.getenv("EMAIL_USERNAME")
            email_pass = os.getenv("EMAIL_PASSWORD")

            print("DEBUG EMAIL USER:", email_user)
            print("DEBUG EMAIL PASS:", "SET" if email_pass else "NOT SET")

            result = send_email(
                to=step.params.get("to"),
                subject=step.params.get("subject"),
                body=state.context.get("email_body", ""),
                username=email_user,
                password=email_pass
            )

            state.context["email_result"] = result

        elif action == "fetch_email_body":
            if "email_body" in state.context:
                result = "Email body ready for sending."
            else:
                result = "Email body missing. Injected subtask should have handled this."

        # =========================================
        # FILE ACTIONS
        # =========================================
        elif action == "read_file":
            content = read_file(step.params.get("path"))
            state.context["file_content"] = content
            result = f"File read: {step.params.get('path')}"

        elif action == "write_file":
            # Check both possible keys the LLM might use
            target_path = params.get("path") or params.get("file_name")
            result = write_file(
                path=target_path,
                content=params.get("content", "")
            )
            state.context["file_written"] = target_path

        # =========================================
        # DATABASE ACTIONS
        # =========================================
        elif action == "query_db":
            # UPDATED: Uses the search_query populated by Data Specialist
            db_result = query_database(params.get("search_query", ""))
            state.context["db_results"] = db_result
            result = f"Database query completed. Found {len(db_result)} records."

        elif action in ["update_db", "insert_project"]:
            # UPDATED: Added support for 'insert_project' alias
            result = write_to_db(
                category=params.get("category", "general"),
                name=params.get("name") or params.get("project_name"),
                details=params.get("details", "")
            )
            state.context["db_status"] = result

        # =========================================
        # SCHEDULER ACTION (UPDATED for Google Calendar Link Sharing)
        # =========================================
        elif action == "schedule_task":
            # EXECUTION: Call the scheduler tool
            result = schedule_task(
                task_name=params.get("task_name"),
                time_str=params.get("time")
            )
            
            # SHARED DATA: We save the full result (containing the link) into context
            state.context["schedule_result"] = result
            # This is what the Body Generator looks for in planner.py
            state.context["scheduled_details"] = result 

        # =========================================
        # UNKNOWN TOOL
        # =========================================
        else:
            raise ValueError(f"No tool implemented for action '{action}'")

        step.status = "done"
        state.execution_logs.append(f"Executed: {action}")

    except Exception as e:
        step.status = "failed"
        state.execution_logs.append(
            f"Execution failed for {action}: {str(e)}"
        )

    # Move to next step
    state.current_step += 1

    # Stop condition
    if state.current_step >= len(state.planned_steps):
        state.finished = True

    return state