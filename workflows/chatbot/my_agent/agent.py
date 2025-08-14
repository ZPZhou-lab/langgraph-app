from langgraph.graph import StateGraph, START, END
from my_agent.utils.state import State
from my_agent.utils.tools import chatbot
from langgraph.checkpoint.memory import InMemorySaver

# build a graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# compile the graph
memory = InMemorySaver()
graph = builder.compile(checkpointer=memory)