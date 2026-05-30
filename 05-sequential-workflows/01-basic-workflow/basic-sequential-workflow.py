from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()


# Define State
class BMIState(TypedDict):
    weight_kg: float
    height_m: float
    bmi: float


def calculate_bmi(state: BMIState) -> BMIState:
    """Calculate the BMI using Weight and Height"""

    wt = state["weight_kg"]
    ht = state["height_m"]

    bmi = wt / (ht**2)
    state["bmi"] = round(bmi, 2)

    return state


# Define graph
graph = StateGraph(BMIState)

# Add node to your graphs
graph.add_node("cal_bmi", calculate_bmi)

# Add Edges
graph.add_edge(START, "cal_bmi")
graph.add_edge("cal_bmi", END)

# Compile
workflow = graph.compile()
print(workflow.get_graph().draw_ascii())

# Execute
initial_state = {"weight_kg": 50, "height_m": 29.2}
final_state = workflow.invoke(initial_state)
pprint(final_state)
