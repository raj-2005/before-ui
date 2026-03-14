from app.graph.state import (
    WorkflowState,
    APPROVAL_NONE,
    APPROVAL_PENDING,
)


# -----------------------------------------
# Risk Classification Node
# -----------------------------------------

def risk_node(state: WorkflowState) -> WorkflowState:
    """
    Evaluates the current step and determines
    whether human approval is required.
    """

    # If finished or no steps, nothing to evaluate
    if state.finished or not state.planned_steps:
        return state

    # Safety check
    if state.current_step >= len(state.planned_steps):
        state.finished = True
        return state

    current_step_obj = state.planned_steps[state.current_step]

    # If step already completed or running, skip
    if current_step_obj.status in ["done", "running"]:
        return state

    risk_level = current_step_obj.risk.lower()

    # Determine approval requirement
    if risk_level in ["medium", "high"]:
        state.approval_status = APPROVAL_PENDING
        state.approval_reason = (
            f"Step '{current_step_obj.action}' "
            f"requires approval (risk: {risk_level})."
        )

        state.execution_logs.append(
            f"Risk detected: {current_step_obj.action} "
            f"requires approval."
        )
    else:
        state.approval_status = APPROVAL_NONE
        state.approval_reason = None

    return state