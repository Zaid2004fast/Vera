import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langgraph.graph import StateGraph, END
from backend.graph.state import VERAState
from backend.agents.guard_agent import guard_node
from backend.agents.response_agent import response_node
from backend.agents.critic_agent import critic_node
from backend.agents.synthesis_agent import synthesis_node

def route_after_guard(state: VERAState) -> str:
    """After the guard, either run the full pipeline or exit immediately."""
    if state["is_cs_question"]:
        return "respond"
    return END

def build_vera_graph():
    graph = StateGraph(VERAState)

    graph.add_node("guard",     guard_node)
    graph.add_node("respond",   response_node)
    graph.add_node("critique",  critic_node)
    graph.add_node("synthesize", synthesis_node)

    graph.set_entry_point("guard")

    # After guard: go to respond if CS, exit if not
    graph.add_conditional_edges(
        "guard",
        route_after_guard,
        {
            "respond": "respond",
            END: END,
        }
    )

    graph.add_edge("respond",    "critique")
    graph.add_edge("critique",   "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()

vera = build_vera_graph()

def run_vera(query: str) -> dict:
    initial_state: VERAState = {
        "query":             query,
        "is_cs_question":    True,
        "retrieved_chunks":  [],
        "initial_response":  "",
        "critic_feedback":   {},
        "final_response":    "",
        "confidence_score":  0.0,
        "in_review_queue":   False,
        "improvements_made": [],
    }
    return vera.invoke(initial_state)