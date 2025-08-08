from langgraph.graph import StateGraph, START, END
from my_agent.utils.state import State
from my_agent.utils.tools import chatbot

# build a graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# compile the graph
graph = builder.compile()