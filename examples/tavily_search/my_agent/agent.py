from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from my_agent.utils.nodes import call_model, should_continue, tool_node
from my_agent.utils.state import AgentState

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["qwen3"]


# define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)
# add nodes
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    "agent",
    # we pass in the function that will determine which node is called next.
    should_continue,
    # a mapping of the return values of `should_continue` to the next node.
    {
        # If `tools`, then we call the tool node.
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# add a normal edge from `action` to `agent`
# This means that after `action` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Compile the graph
graph = workflow.compile()