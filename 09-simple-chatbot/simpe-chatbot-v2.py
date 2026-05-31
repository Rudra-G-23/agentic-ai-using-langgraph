import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from rich import print
from rich.panel import Panel
from rich.pretty import pprint
from rich.traceback import install

install()
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


model = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=100,
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):

    messages = state["messages"]

    response = model.invoke(messages)

    return {"messages": [response]}


checkpointer = MemorySaver()


graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
print(chatbot.get_graph().print_ascii())
print(chatbot.get_graph().draw_mermaid())

thread_id = "rudra-chat-thread"
config = {"configurable": {"thread_id": thread_id}}


print(
    Panel.fit(
        "[bold cyan]LangGraph Chat Started[/bold cyan]\n"
        "Type [bold yellow]exit[/bold yellow] to stop.",
        border_style="green",
    )
)

while True:
    user_message = input("\n[You] > ")

    if user_message.strip().lower() in [
        "exit",
        "quit",
        "bye",
        "stop",
    ]:
        print("\n[bold red]Chat Ended[/bold red]")
        break

    response = chatbot.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
    )

    ai_message = response["messages"][-1].content

    print(
        Panel(
            ai_message, title="[bold magenta]AI[/bold magenta]", border_style="magenta"
        )
    )

    print("\n[bold green]========= FULL STATE =========[/bold green]")

    state_snapshot = chatbot.get_state(config)

    all_messages = state_snapshot.values["messages"]

    for i, msg in enumerate(all_messages, start=1):
        if isinstance(msg, HumanMessage):
            role = "USER"

        elif isinstance(msg, AIMessage):
            role = "AI"

        else:
            role = "OTHER"

        print(f"[bold cyan]{i}. {role}[/bold cyan] -> {msg.content}")

    print("\n[bold yellow]========= JSON FORMAT =========[/bold yellow]")

    history_json = []

    for msg in all_messages:
        history_json.append(
            {
                "type": msg.type,
                "content": msg.content,
            }
        )

    pprint(history_json)

    # Optional Raw JSON
    # print(json.dumps(history_json, indent=4))
