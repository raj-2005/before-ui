from langgraph.graph import StateGraph, END

from app.graph.state import WorkflowState
# Added data_specialist_node to imports
from app.graph.nodes.planner import planner_node, body_generator_node, data_specialist_node 
from app.graph.nodes.subtask import subtask_node
from app.graph.nodes.risk import risk_node
from app.graph.nodes.approval import approval_node
from app.graph.nodes.executor import executor_node

# -----------------------------------------
# Graph Builder
# -----------------------------------------

def build_graph():
    graph = StateGraph(WorkflowState)

    # 1. Register ALL Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("subtask", subtask_node)
    graph.add_node("body_gen", body_generator_node)
    graph.add_node("data_prep", data_specialist_node) # <--- New Data Specialist Node
    graph.add_node("risk", risk_node)
    graph.add_node("approval", approval_node)
    graph.add_node("executor", executor_node)

    # 2. Define the Flow
    graph.set_entry_point("planner")

    # Flow: Planner -> Subtask -> Body Gen -> Data Prep -> Risk
    graph.add_edge("planner", "subtask")
    graph.add_edge("subtask", "body_gen") 
    graph.add_edge("body_gen", "data_prep") # <--- Chain the new node here
    graph.add_edge("data_prep", "risk")     # Once all content is ready, assess risk

    # 3. Risk -> Conditional Routing (Approval or Executor)
    graph.add_conditional_edges(
        "risk",
        route_after_risk,
        {
            "approval": "approval",
            "executor": "executor",
        },
    )

    # 4. Approval -> Executor (If approved, execute)
    graph.add_edge("approval", "executor")

    # 5. Executor -> Loop back or End
    graph.add_conditional_edges(
        "executor",
        route_after_execution,
        {
            "continue": "subtask", 
            "end": END,
        },
    )

    return graph.compile()


# -----------------------------------------
# Routing Functions
# -----------------------------------------

def route_after_risk(state: WorkflowState) -> str:
    if state.approval_status == "pending":
        return "approval"
    return "executor"


def route_after_execution(state: WorkflowState) -> str:
    if state.finished:
        return "end"
    return "continue"