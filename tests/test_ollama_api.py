"""
Ollama is free to used, But hard to used.
I can't run through the api.
"""

import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from rich.console import Console
from rich.pretty import pprint
from rich.traceback import install

load_dotenv()
install(show_locals=True)
console = Console()

# Retrieve your API credentials from your .env file
# Ensure your OLLAMA_BASE_URL looks like "http://your-server-ip:11434" or "https://yourdomain.com"
api_url = os.getenv("OLLAMA_API_KEY", "http://localhost:11434")

llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0.0,
    base_url=api_url,
)

# response = llm.invoke("What is the capital of India?")
# pprint(response.content)

try:
    response = llm.invoke("What is the capital of India?")
    pprint("Response from API:")
    pprint(response.content)
except Exception as e:
    console.print(f"Failed to connect to the Ollama API. Error: {e}")
