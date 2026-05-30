from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()
load_dotenv()


@dataclass(frozen=True)
class ModelConfig:
    DEFAULT_MODEL: ClassVar[str] = "llama-3.1-8b-instant"
    MAX_RETRIES: ClassVar[int] = 3
    TEMPERATURE: ClassVar[float] = 0.7

    max_outline_tokens: int = 20
    max_blog_tokens: int = 200


# State definition
class BlogState(TypedDict):
    topic: str
    outline: str
    blog: str


# Node Key
class NodeKey(str, Enum):
    GENERATE_OUTLINE = "generate_outline"
    GENERATE_BLOG = "generate_blog"


# Model
def get_llm(max_tokens: int = 1000) -> ChatGroq:
    """Create LLM instances."""
    return ChatGroq(
        model=ModelConfig.DEFAULT_MODEL,
        temperature=ModelConfig.TEMPERATURE,
        max_retries=ModelConfig.MAX_RETRIES,
        max_tokens=max_tokens,
    )


def get_outline(state: BlogState) -> dict[str, Any]:
    """Generate the Outline"""

    topic = state.get("topic")
    if not topic:
        raise ValueError("Can't generate outline: 'topic' is missing")

    model = get_llm(max_tokens=ModelConfig.max_outline_tokens)

    messages = [
        SystemMessage(
            content="You are an expert technical content strategist. Create clean, structured outlines."
        ),
        HumanMessage(f"Create a comprehensive blog outline on topic: {topic}"),
    ]

    response = model.invoke(messages)
    return {"outline": str(response.content)}


def gen_blog(state: BlogState) -> dict[str, Any]:

    outline = state.get("outline")

    model = get_llm(max_tokens=ModelConfig.max_blog_tokens)

    messages = [
        HumanMessage(
            "You are a professional tech blogger. Expand outlines into highly accurate articles."
        ),
        HumanMessage(
            f"Write a full, high-quality blog post based on this outline: \n\n\n{outline}"
        ),
    ]

    response = model.invoke(messages)
    return {"blog": str(response.content)}


def create_workflow() -> StateGraph:
    graph = StateGraph(BlogState)

    # Add Node
    graph.add_node(NodeKey.GENERATE_OUTLINE, get_outline)
    graph.add_node(NodeKey.GENERATE_BLOG, gen_blog)

    # Add Edges
    graph.add_edge(START, NodeKey.GENERATE_OUTLINE)
    graph.add_edge(NodeKey.GENERATE_OUTLINE, NodeKey.GENERATE_BLOG)
    graph.add_edge(NodeKey.GENERATE_BLOG, END)

    # Compile
    return graph.compile()


if __name__ == "__main__":
    workflow = create_workflow()

    try:
        initial_state: BlogState = {
            "topic": "Quantum Computing Basics",
            "outline": "",
            "blog": "",
        }
        final_state = workflow.invoke(initial_state)

        pprint("\n\n[bold green] Final Output State: [/bold green]")
        pprint(final_state)

    except Exception as e:
        print(f"[bold red] Pipeline Execution Failed:[/bold red] {e}")
