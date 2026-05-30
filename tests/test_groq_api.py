import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from rich.pretty import pprint

load_dotenv()
os.getenv("GROQ_API_KEY")

# Initialize the Groq model
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.1, max_tokens=20)

# Invoke the model with a prompt
response = llm.invoke("what is money")
pprint(response.content)
