import operator
from dataclasses import dataclass
from enum import Enum
from typing import Annotated, ClassVar, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from rich import print
from rich.pretty import pprint
from rich.traceback import install

# Initialise environment and rich logging
install()
load_dotenv()


# Configuration
@dataclass(frozen=True)
class ModelConfig:
    DEFAULT_MODEL: ClassVar[str] = "llama-3.1-8b-instant"
    MAX_RETRIES: ClassVar[int] = 3
    TEMPERATURE: ClassVar[float] = 0.2
    MAX_TOKENS: ClassVar[int] = 500


# Output Schemas
class EvaluationSchema(BaseModel):
    feedback: str = Field(
        description="Detailed text feedback explaining the quality of the essay section."
    )
    score: int = Field(
        description="An integer score from 1 to 10 based strictly on your evaluation."
    )


# Graph State
class ReviewTextState(TypedDict):
    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    overall_feedback: str
    individual_scores: Annotated[list[int], operator.add]
    avg_score: float


# Initialize Models
model = ChatGroq(
    model=ModelConfig.DEFAULT_MODEL,
    max_retries=ModelConfig.MAX_RETRIES,
    temperature=ModelConfig.TEMPERATURE,
    max_tokens=ModelConfig.MAX_TOKENS,
)

# Use 'json_object' or 'tool_calls' structure mapping
structured_model = model.with_structured_output(EvaluationSchema)


# Node Enums
class NodeKey(str, Enum):
    EVALUATE_LANGUAGE = "evaluate_language"
    EVALUATE_ANALYSIS = "evaluate_analysis"
    EVALUATE_THOUGHT = "evaluate_thought"
    EVALUATE_FINAL = "final_evaluation"


# Helper for system messages to enforce tool parameters
def build_messages(criteria: str, essay: str) -> list:
    return [
        SystemMessage(
            content=(
                "You are an expert essay grader. You must output structured data matching the schema perfectly. "
                "Provide your clear text feedback in the 'feedback' property. "
                "Provide ONLY a single, raw integer value between 1 and 10 in the 'score' property. "
                "Do NOT include text like 'Score: 8/10' inside the feedback block."
            )
        ),
        HumanMessage(
            content=f"Evaluate the essay focusing strictly on: {criteria}.\n\nEssay:\n{essay}"
        ),
    ]


# Node Functions
def evaluate_lang(state: ReviewTextState) -> dict:
    essay = state.get("essay")
    messages = build_messages(
        "grammar, vocabulary, mechanics, and language quality", essay
    )
    output = structured_model.invoke(messages)
    return {"language_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_analysis(state: ReviewTextState) -> dict:
    essay = state.get("essay")
    messages = build_messages(
        "depth of argument, critical insights, and content analysis", essay
    )
    output = structured_model.invoke(messages)
    return {"analysis_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_thought(state: ReviewTextState) -> dict:
    essay = state.get("essay")
    messages = build_messages(
        "structural clarity, logical flow, transitions, and organization of thoughts",
        essay,
    )
    output = structured_model.invoke(messages)
    return {"clarity_feedback": output.feedback, "individual_scores": [output.score]}


def evaluate_final(state: ReviewTextState) -> dict:
    scores = state.get("individual_scores", [])
    avg = sum(scores) / len(scores) if scores else 0.0

    summary_prompt = (
        f"Consolidate these evaluation summaries into one final verdict paragraph:\n"
        f"Language Feedback: {state.get('language_feedback')}\n"
        f"Analysis Feedback: {state.get('analysis_feedback')}\n"
        f"Clarity Feedback: {state.get('clarity_feedback')}"
    )
    output = model.invoke([HumanMessage(content=summary_prompt)])

    return {"overall_feedback": output.content, "avg_score": round(avg, 2)}


# Build Workflow Graph
graph = StateGraph(ReviewTextState)

# Add Nodes
graph.add_node(NodeKey.EVALUATE_LANGUAGE, evaluate_lang)
graph.add_node(NodeKey.EVALUATE_ANALYSIS, evaluate_analysis)
graph.add_node(NodeKey.EVALUATE_THOUGHT, evaluate_thought)
graph.add_node(NodeKey.EVALUATE_FINAL, evaluate_final)

# Parallel Execution setup from START
graph.add_edge(START, NodeKey.EVALUATE_LANGUAGE)
graph.add_edge(START, NodeKey.EVALUATE_ANALYSIS)
graph.add_edge(START, NodeKey.EVALUATE_THOUGHT)

# Fan-in into Final evaluation
graph.add_edge(NodeKey.EVALUATE_LANGUAGE, NodeKey.EVALUATE_FINAL)
graph.add_edge(NodeKey.EVALUATE_ANALYSIS, NodeKey.EVALUATE_FINAL)
graph.add_edge(NodeKey.EVALUATE_THOUGHT, NodeKey.EVALUATE_FINAL)
graph.add_edge(NodeKey.EVALUATE_FINAL, END)

workflow = graph.compile()

# Target Essay Input
ESSAY_TEXT = """The Paradox of FailureIn a society obsessed with flawless achievements, failure is often treated as a source of shame or a definitive end. However, looking at the trajectory of any successful endeavor reveals a different story. Every misstep carries an invaluable lesson, acting as a profound teacher. When we fail, we are given a rare opportunity to pause, evaluate our methods, and ask a critical question: What went wrong? This analytical process transforms a painful setback into a rich well of experience.Building Resilience and CharacterBeyond acquiring new knowledge, failure builds resilience. It tests our emotional endurance and teaches us how to navigate disappointment. As Winston Churchill famously noted, success consists of "going from failure to failure without losing enthusiasm." Those who experience hardship and choose to rise again develop a strong character. They become more humble, adaptable, and prepared for future adversities.Stepping Stone to InnovationMany of the world's greatest discoveries and artistic masterpieces are the direct result of trial and error. Scientists, inventors, and entrepreneurs constantly test boundaries, knowing that many attempts will not yield results. Each failed experiment or discarded draft eliminates what does not work, narrowing down the path to the right solution. In this way, failure is an active, constructive force in the process of creation.Redefining PerspectivePerhaps the most powerful aspect of failure is its ability to alter our perspective. When we stumble, we are forced to re-examine our goals and our approach to them. It strips away overconfidence and allows us to build a more grounded, realistic strategy.Ultimately, accepting failure as a natural part of the journey allows us to let go of the paralyzing fear of making mistakes. By shifting our mindset, we begin to see that a fall is not a defeat, but an invitation to try again with greater wisdom and determination."""

# Execution
if __name__ == "__main__":
    print("\n[bold blue]Running Evaluation Workflow...[/bold blue]")
    initial_state = {"essay": ESSAY_TEXT, "individual_scores": []}
    final_state = workflow.invoke(initial_state)

    print("\n[bold green]Final Evaluation State Output:[/bold green]")
    pprint(final_state)
