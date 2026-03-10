from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import scout_node, skeptic_node, writer_node, human_review
from langgraph.checkpoint.memory import MemorySaver


def route_after_skeptic(state: AgentState):
    if state.iteration_count >= 3:
        print(f"Max iterations ({state.iteration_count}) reached. Escalating to human review.")
        return "human_review"

    # Hard override: if we've looped twice and quality is decent, stop forcing more research
    if state.iteration_count >= 2 and (state.skeptic_notes or "") and state.is_satisfactory is False:
        print(f"Iteration {state.iteration_count} reached with no satisfaction — escalating anyway.")
        return "human_review"

    if state.is_satisfactory:
        print("Research auto-verified. Sending to human for final sign-off.")
        return "human_review"

    print(f"Research insufficient (Attempt {state.iteration_count}). Re-routing to Scout...")
    return "scout"


def route_after_human(state: AgentState):
    """
    After human reviews:
    - approve  → proceed to writer
    - reject   → send back to scout for revision
    """
    if state.human_verdict == "approve":
        print("Human approved. Proceeding to writer.")
        return "writer"
    if state.human_verdict in ("reject", "comment"):
        print(f"Human {state.human_verdict}. Sending back to scout.")
        return "scout"
    print(f"Unknown verdict '{state.human_verdict}'. Defaulting to scout.")
    return "scout"


memory = MemorySaver()
workflow = StateGraph(AgentState)

workflow.add_node("scout", scout_node)
workflow.add_node("skeptic", skeptic_node)
workflow.add_node("human_review", human_review)
workflow.add_node("writer", writer_node)

workflow.add_edge(START, "scout")
workflow.add_edge("scout", "skeptic")

workflow.add_conditional_edges(
    "skeptic",
    route_after_skeptic,
    {"scout": "scout", "human_review": "human_review"}
)

workflow.add_conditional_edges(
    "human_review",
    route_after_human,
    {"writer": "writer", "scout": "scout"}
)

workflow.add_edge("writer", END)

app = workflow.compile(checkpointer=memory)
