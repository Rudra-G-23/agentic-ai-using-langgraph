import os

from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from rich.pretty import pprint

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Alternative active model: Qwen/Qwen2.5-Coder-7B-Instruct
# or meta-llama/Llama-3.1-8B-Instruct
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-Coder-7B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=huggingface_api_key,
    max_new_tokens=20,
)

chat_model = ChatHuggingFace(llm=llm)
response = chat_model.invoke("Why love is important")
pprint(response)
