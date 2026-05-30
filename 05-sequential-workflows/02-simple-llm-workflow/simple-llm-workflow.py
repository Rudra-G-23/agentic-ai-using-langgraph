from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()
load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant", max_tokens=20)


# Define State
class SimpleLLMState(TypedDict):
    question: str
    answer: str


# Define Graph
graph = StateGraph(SimpleLLMState)


# Edges Function
def llm_qa(state: SimpleLLMState) -> dict:
    question = state["question"]
    prompt = f"Answer the following question: {question}"
    answer = model.invoke(prompt).content

    return {"answer": answer}


# Add Node
graph.add_node("simple_llm", llm_qa)

# Add Edges
graph.add_edge(START, "simple_llm")
graph.add_edge("simple_llm", END)

# Compile
workflow = graph.compile()
print(workflow.get_graph().print_ascii())

# Execute
initial_state = {"question": "what is quantum physic"}
final_state = workflow.invoke(initial_state)
pprint(final_state)
