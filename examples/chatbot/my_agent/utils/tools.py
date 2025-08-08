from langchain_ollama import ChatOllama
from .state import State

def chatbot(state: State):
    """
    a simple chatbot function that uses the ChatOllama model to respond to messages.
    """
    # create a ChatOllama instance
    llm = ChatOllama(model='qwen3:8b', reasoning=False)
    return {"messages": [llm.invoke(state["messages"])]}