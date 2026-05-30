from enum import Enum
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()


class BatsmanState(TypedDict):
    runs: int
    balls: int
    fours: int
    sixes: int
    sr: float
    bpd: float
    boundary_pct: float
    summary: str


class NodeKey(str, Enum):
    GENERATE_SR = "generate_sr"
    GENERATE_BPD = "generate_bpd"
    GENERATE_BOUNDARY_PCT = "generate_boundary_pct"
    GENERATE_SUMMARY = "generate_summary"


graph = StateGraph(BatsmanState)


def calculate_sr(state: BatsmanState) -> dict:
    runs, balls = state.get("runs", 0), state.get("balls", 1)
    sr = (runs / balls) * 100
    return {"sr": sr}


def calculate_bpd(state: BatsmanState) -> dict:
    balls = state.get("balls", 0)
    boundaries = state.get("fours", 0) + state.get("sixes", 0)
    bpd = balls / boundaries if boundaries > 0 else float("inf")
    return {"bpd": bpd}


def calculate_boundary_pct(state: BatsmanState) -> dict:
    runs = state.get("runs", 1)
    fours = state.get("fours", 0)
    sixes = state.get("sixes", 0)
    bound_runs = (fours * 4) + (sixes * 6)
    bound_pct = (bound_runs / runs) * 100
    return {"boundary_pct": bound_pct}


def summary(state: BatsmanState) -> dict:
    summary_text = f"""
    Strike Rate: {state.get("sr"):.2f} 
    Balls per boundary: {state.get("bpd"):.2f}
    Boundary Pct: {state.get("boundary_pct"):.2f}%
    """
    return {"summary": summary_text.strip()}


graph.add_node(NodeKey.GENERATE_SR, calculate_sr)
graph.add_node(NodeKey.GENERATE_BPD, calculate_bpd)
graph.add_node(NodeKey.GENERATE_BOUNDARY_PCT, calculate_boundary_pct)
graph.add_node(NodeKey.GENERATE_SUMMARY, summary)

graph.add_edge(START, NodeKey.GENERATE_SR)
graph.add_edge(START, NodeKey.GENERATE_BOUNDARY_PCT)
graph.add_edge(START, NodeKey.GENERATE_BPD)

graph.add_edge(NodeKey.GENERATE_SR, NodeKey.GENERATE_SUMMARY)
graph.add_edge(NodeKey.GENERATE_BOUNDARY_PCT, NodeKey.GENERATE_SUMMARY)
graph.add_edge(NodeKey.GENERATE_BPD, NodeKey.GENERATE_SUMMARY)

graph.add_edge(NodeKey.GENERATE_SUMMARY, END)

workflow = graph.compile()
print(workflow.get_graph().draw_ascii())
print(workflow.get_graph().draw_mermaid())

initial_state = {"runs": 100, "balls": 50, "fours": 6, "sixes": 4}

final_state = workflow.invoke(initial_state)
pprint(final_state)
