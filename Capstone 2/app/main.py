# app/main.py

from app.graph.graph import build_graph
from app.graph.state import WorkflowState


def run_workflow(intent: str):

    app_graph = build_graph()

    state = WorkflowState(user_intent=intent)

    print("\n🚀 Starting Workflow\n")

    result = app_graph.invoke(state)

    print("DEBUG RESULT:", result)

    # ✅ Convert returned dict back into WorkflowState
    final_state = WorkflowState(**result)

    if final_state.execution_logs:
        for log in final_state.execution_logs:
            print("📝", log)

    print("\n✅ Workflow Finished")
    print("Final Context:", final_state.context)
    print("Execution Logs:", final_state.execution_logs)


if __name__ == "__main__":

    user_intent = input("Enter your workflow intent: ")

    run_workflow(user_intent)