from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()
load_dotenv()


@dataclass(frozen=True)
class ModelConfig:
    DEFAULT_MODEL: ClassVar[str] = "llama-3.1-8b-instant"
    MAX_RETRIES: ClassVar[int] = 3
    TEMPERATURE: ClassVar[float] = 0.2
    MAX_TOKENS: ClassVar[int] = 100


class EvaluationSchema(BaseModel):
    sentiment: str = Field(
        description="The sentiment classification of the user feedback. Must be strictly 'positive' or 'negative'."
    )


class ReviewTextState(TypedDict):
    user_review: str
    sentiment: str
    positive_response_reply: str
    negative_response_reply: str


model = ChatGroq(
    model=ModelConfig.DEFAULT_MODEL,
    max_retries=ModelConfig.MAX_RETRIES,
    temperature=ModelConfig.TEMPERATURE,
    max_tokens=ModelConfig.MAX_TOKENS,
)

# Use structured output mapping
structured_model = model.with_structured_output(EvaluationSchema)


# Node Enums
class NodeKey(str, Enum):
    EVALUATE_SENTIMENT = "evaluate_sentiment"
    NEGATIVE_RESPONSE = "negative_response"
    POSITIVE_RESPONSE = "positive_response"


def evaluate_sentiment_node(state: ReviewTextState) -> dict:
    """Uses LLM structured output to classify user review sentiment."""
    system_prompt = """You are an expert sentiment analyzer. Classify the user review text exactly
        as either 'positive' or 'negative' based on its tone.
        """
    # Invoke structured model
    result: EvaluationSchema = structured_model.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=state["user_review"]),
        ]
    )
    # Clean output to match expectation
    sentiment = result.sentiment.strip().lower()
    return {"sentiment": sentiment}


def positive_response_node(state: ReviewTextState) -> dict:
    """Generates a thankful reply for a positive review."""
    prompt = f"Write a one-sentence polite thank you reply to this customer review: {state['user_review']}"
    response = model.invoke([HumanMessage(content=prompt)])
    return {"positive_response_reply": response.content}


def negative_response_node(state: ReviewTextState) -> dict:
    """Generates an apologetic reply for a negative review."""
    prompt = f"Write a one-sentence polite, apologetic customer service reply to this bad review: {state['user_review']}"
    response = model.invoke([HumanMessage(content=prompt)])
    return {"negative_response_reply": response.content}


def route_sentiment(state: ReviewTextState) -> str:
    """Determines which response node to trigger next based on state data."""
    if state.get("sentiment") == "positive":
        return NodeKey.POSITIVE_RESPONSE.value
    else:
        return NodeKey.NEGATIVE_RESPONSE.value


workflow = StateGraph(ReviewTextState)

# Add processing nodes
workflow.add_node(NodeKey.EVALUATE_SENTIMENT.value, evaluate_sentiment_node)
workflow.add_node(NodeKey.POSITIVE_RESPONSE.value, positive_response_node)
workflow.add_node(NodeKey.NEGATIVE_RESPONSE.value, negative_response_node)

# Add start edge
workflow.add_edge(START, NodeKey.EVALUATE_SENTIMENT.value)

# Add conditional routing edges
workflow.add_conditional_edges(
    NodeKey.EVALUATE_SENTIMENT.value,
    route_sentiment,
    {
        NodeKey.POSITIVE_RESPONSE.value: NodeKey.POSITIVE_RESPONSE.value,
        NodeKey.NEGATIVE_RESPONSE.value: NodeKey.NEGATIVE_RESPONSE.value,
    },
)

# Connect endpoints to end execution
workflow.add_edge(NodeKey.POSITIVE_RESPONSE.value, END)
workflow.add_edge(NodeKey.NEGATIVE_RESPONSE.value, END)

# Compile workflow app
app = workflow.compile()

# Render graph layout
print("[bold cyan]Graph Execution Workflow:[/bold cyan]")
app.get_graph().print_ascii()
print(app.get_graph().draw_mermaid())

# Run a test execution case
initial_input = {
    "user_review": "The application crashes immediately upon launch on my phone. Very frustrating experience.",
    "sentiment": "",
    "positive_response_reply": "",
    "negative_response_reply": "",
}

print("\n[bold green]Initial Review State:[/bold green]")
pprint(initial_input)

final_state = app.invoke(initial_input)

print("\n[bold magenta]Final Output State:[/bold magenta]")
pprint(final_state)
