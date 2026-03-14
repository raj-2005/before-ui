from typing import List , Dict , TypedDict , Any , Optional
from pydantic import BaseModel , Field


# Action (single workflow step) , every action has these information inside of it
class Action(BaseModel):
    """
    Every action has these information inside of it, what is the name of the action , what parameters it needs to run , how risky is it and what is the status of it
    """
    action : str             # e.g send email , fetch data
    params : Dict[str, Any] = Field(default_factory=dict)
    risk : str = "low"       # low|medium|high
    status : str = "pending" # pending | running | done | failed


# approval status ENUM like values
APPROVAL_NONE = "none"
APPROVAL_PENDING = "pending"
APPROVAL_APPROVED = "approved"
APPROVAL_REJECTED = "rejected"



# Main Workflow State

class WorkflowState(BaseModel):

    # original user request in natural language
    user_intent : str

    # planned workflow steps (actions) to achieve the user intent
    planned_steps : List[Action] = Field(default_factory=list)

    # Pointer to current step index
    current_step : int = 0

    # context data collected during execution (e.g. API responses, data drom db)
    context : Dict[str, Any] = Field(default_factory=dict)

    # approval tracking
    approval_status : str = APPROVAL_NONE # at the beginning there is no approval needed , but if the workflow has a high risk step then it will be set to pending and wait for user approval
    approval_reason : Optional[str] = None # if approval is rejected , this field can store the reason for rejection




    # execution logs for audit / debug /dashboard
    execution_logs : List[str] = Field(default_factory=list)


    # final workflow result
    finished : bool = False
    error : Optional[str] = None # if there is an error during execution , this field can store the error message



# Helper create initial state

def create_initial_state(user_intent : str) -> WorkflowState:
    """
    This function creates the initial state of the workflow based on the user intent for execution.
    """
    return WorkflowState(user_intent=user_intent)