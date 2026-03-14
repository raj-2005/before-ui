from app.graph.state import (
    WorkflowState,
    APPROVAL_PENDING,
    APPROVAL_APPROVED,
    APPROVAL_REJECTED,
    APPROVAL_NONE,
)


# -----------------------------------------
# Approval Gate Node
# -----------------------------------------

def approval_node(state: WorkflowState) -> WorkflowState:
    """
    Handles human-in-the-loop approval logic.
    Pauses execution if approval is pending.
    Resumes or terminates based on user decision.
    """

    # If workflow already finished, return
    if state.finished:
        return state

    # If no approval needed, continue normally
    if state.approval_status == APPROVAL_NONE:
        return state

    # If approval still pending, pause execution
    if state.approval_status == APPROVAL_PENDING:
        state.execution_logs.append(
            "Execution paused. Awaiting user approval."
        )
        return state  # Graph should wait here

    # If user approved
    if state.approval_status == APPROVAL_APPROVED:
        state.execution_logs.append("User approved execution.")
        state.approval_status = APPROVAL_NONE
        state.approval_reason = None
        return state

    # If user rejected
    if state.approval_status == APPROVAL_REJECTED:
        state.execution_logs.append("User rejected execution.")
        state.finished = True
        return state

    return state