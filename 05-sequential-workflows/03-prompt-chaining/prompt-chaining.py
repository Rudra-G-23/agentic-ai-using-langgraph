from enum import Enum
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
class BlogState(TypedDict):
    topic: str
    outline: str
    blog: str


# Define Graph
graph = StateGraph(BlogState)


# Node Key
class NodeKey(str, Enum):
    GENERATE_OUTLINE = "generate_outline"
    GENERATE_BLOG = "generate_blog"


# Edges Function
def gen_outline(state: BlogState) -> dict:
    topic = state["topic"]
    query = f"Create a outline based on this topic: {topic}"
    outline = model.invoke(query).content
    return {"outline": outline}


def gen_blog(state: BlogState) -> dict:
    outline = state["outline"]
    query = f"Create a blog post on give outline: {outline}"
    blog = model.invoke(query).content
    return {"blog": blog}


# Add Node
graph.add_node(NodeKey.GENERATE_OUTLINE, gen_outline)
graph.add_node(NodeKey.GENERATE_BLOG, gen_blog)

# Add Edges
graph.add_edge(START, NodeKey.GENERATE_OUTLINE)
graph.add_edge(NodeKey.GENERATE_OUTLINE, NodeKey.GENERATE_BLOG)
graph.add_edge(NodeKey.GENERATE_BLOG, END)

# Compile
workflow = graph.compile()
print(workflow.get_graph().print_ascii())

# Execute
initial_state = {"topic": "quantum physic"}
final_state = workflow.invoke(initial_state)
pprint(final_state)
