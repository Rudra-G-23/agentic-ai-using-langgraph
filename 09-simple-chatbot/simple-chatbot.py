import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from rich import print
from rich.pretty import pprint
from rich.traceback import install

install()
load_dotenv()
os.getenv("GROQ_API_KEY")

model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_tokens=20)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    query = state.get("messages")
    response = model.invoke(query)
    return {"messages": [response]}


checkpointer = MemorySaver()
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
# print(chatbot.get_graph().draw_ascii())
# print(chatbot.get_graph().draw_mermaid())

# initial_state = {"messages": [HumanMessage(content="hello my name is rudra")]}
# final_state = chatbot.invoke(initial_state)
# pprint(final_state)

print("\n\n[bold blue] Chat with AI [/bold blue]")

thread_id = "1"

while True:
    user_message = input("\n\nType here: ")
    pprint(f"\n<|User|>: {user_message}")

    if user_message.strip().lower() in ["exit", "stop", "bye"]:
        break

    config = {"configurable": {"thread_id": thread_id}}

    response = chatbot.invoke(
        {"messages": HumanMessage(content=user_message)}, config=config
    )
    pprint(f"<|AI|>: {response['messages'][-1].content}")
