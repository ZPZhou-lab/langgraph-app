
from typing import Literal, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    llm_output: str
    decision: str

# mock chatbot node
def chatbot(state: State) -> State:
    return {'llm_output': "Here is a llm response message"}

# human decision node
def human_decision(state: State) -> Command[Literal['approved_node', 'rejected_node']]:
    decision = interrupt({
        "question": "Do you approve the LLM response?",
        "llm_output": state['llm_output']
    })

    if decision == "approve":
        return Command(goto="approved_node", update={"decision": "approved"})
    else:
        return Command(goto="rejected_node", update={"decision": "rejected"})

# next node after human decision
def approved_node(state: State) -> State:
    print("✅The node after human decision is approved.")
    return state

def rejected_node(state: State) -> State:
    print("❌The node after human decision is rejected.")
    return state

# build a graph
builder = StateGraph(State)

# add nodes
builder.add_node("chatbot", chatbot)
builder.add_node("human_decision", human_decision)
builder.add_node("approved_node", approved_node)
builder.add_node("rejected_node", rejected_node)

# set the graph edges
builder.set_entry_point("chatbot")
builder.add_edge("chatbot", "human_decision")
builder.add_edge("approved_node", END)
builder.add_edge("rejected_node", END)

# compile the graph
graph = builder.compile(checkpointer=None)