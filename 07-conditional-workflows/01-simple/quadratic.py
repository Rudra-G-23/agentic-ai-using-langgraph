from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()


# 1. Define the State
class QuadraticState(TypedDict):
    a: int
    b: int
    c: int
    equation: str
    discriminator: float
    result: str


# 2. Define the Nodes
def show_eq(state: QuadraticState) -> dict:
    a, b, c = state["a"], state["b"], state["c"]
    # Simple formatting for the equation string
    eq_str = f"{a}x² + ({b})x + ({c}) = 0"
    return {"equation": eq_str}


def cal_disc(state: QuadraticState) -> dict:
    a, b, c = state["a"], state["b"], state["c"]
    # Formula: b² - 4ac
    disc = (b**2) - (4 * a * c)
    return {"discriminator": disc}


def handle_positive(state: QuadraticState) -> dict:
    return {"result": "Two distinct real roots exist."}


def handle_zero(state: QuadraticState) -> dict:
    return {"result": "One repeated real root exists."}


def handle_negative(state: QuadraticState) -> dict:
    return {"result": "Two complex/imaginary roots exist."}


# 3. Define the Conditional Routing Logic
def route_by_discriminant(state: QuadraticState) -> str:
    disc = state["discriminator"]
    if disc > 0:
        return "positive"
    elif disc == 0:
        return "zero"
    else:
        return "negative"


# 4. Build the Graph
workflow = StateGraph(QuadraticState)

# Add all nodes
workflow.add_node("show_eq", show_eq)
workflow.add_node("cal_disc", cal_disc)
workflow.add_node("handle_positive", handle_positive)
workflow.add_node("handle_zero", handle_zero)
workflow.add_node("handle_negative", handle_negative)

# Add linear edges
workflow.add_edge(START, "show_eq")
workflow.add_edge("show_eq", "cal_disc")

# Add the 3-way conditional edges
workflow.add_conditional_edges(
    "cal_disc",
    route_by_discriminant,
    {
        "positive": "handle_positive",
        "zero": "handle_zero",
        "negative": "handle_negative",
    },
)

# Connect conditional endpoints to the end
workflow.add_edge("handle_positive", END)
workflow.add_edge("handle_zero", END)
workflow.add_edge("handle_negative", END)

# Compile graph
app = workflow.compile()

# 5. Display the ASCII Graph
print("[bold cyan]Graph Structure:[/bold cyan]")
app.get_graph().print_ascii()
print(app.get_graph().draw_mermaid())

# 6. Execute with Initial and Final States
initial_state = {"a": 1, "b": -5, "c": 6}

print("\n[bold green]Initial Input State:[/bold green]")
pprint(initial_state)

final_output = app.invoke(initial_state)

print("\n[bold magenta]Final State After Execution:[/bold magenta]")
pprint(final_output)
