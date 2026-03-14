from app.graph.state import WorkflowState, Action


# -----------------------------------------
# Define Context Requirements Per Action
# -----------------------------------------

REQUIRED_CONTEXT = {
    "send_email": ["email_body"],
    "summarize_data": ["raw_data"],
}


# -----------------------------------------
# Subtask Discovery Node
# -----------------------------------------

def subtask_node(state: WorkflowState) -> WorkflowState:
    """
    Detects missing context for the current step
    and dynamically injects prerequisite steps if required.
    """

    # If workflow finished or no steps
    if state.finished or not state.planned_steps:
        return state

    # Safety check: avoid index error
    if state.current_step >= len(state.planned_steps):
        state.finished = True
        return state

    current_step_obj = state.planned_steps[state.current_step]
    action = current_step_obj.action

    # Check if action has required context
    if action in REQUIRED_CONTEXT:
        required_keys = REQUIRED_CONTEXT[action]

        for key in required_keys:
            # ✅ FIXED HERE
            if key not in state.context:

                # Inject a new step BEFORE current step
                injected_step = Action(
                    action=f"fetch_{key}",
                    params={},
                    risk="low",
                    status="pending"
                )

                state.planned_steps.insert(state.current_step, injected_step)

                state.execution_logs.append(
                    f"Subtask injected: fetch_{key} before {action}"
                )

                return state

    return state