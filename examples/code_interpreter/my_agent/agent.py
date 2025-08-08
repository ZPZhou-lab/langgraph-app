from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.checkpoint.memory import InMemorySaver
from my_agent.utils.state import State
from my_agent.utils.nodes import chatbot, tools, route_tools

# build a graph
builder = StateGraph(State)

# add nodes
builder.add_node("chatbot", chatbot)
builder.add_node("tools", tools)

# set the graph edges
builder.set_entry_point("chatbot")
builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {
        "tools": "tools",
        END: END
    }
)
# when tools are called, go back to the chatbot
builder.add_edge("tools", "chatbot")

# compile the graph
# memory = InMemorySaver()
graph = builder.compile(checkpointer=None)

# if __name__ == "__main__":
#     # while True:
#     # get user input
#     thread_id = "1"
#     user_input = "我需要一些专家指导来帮助我构建一个 AI Agent 系统，你可以帮我询问专家吗？"

#     if user_input.lower() == "exit":
#         print("========== Bye ==========")

#     events = graph.stream(
#         {'messages': [{'role': 'user', 'content': user_input}]},
#         {'configurable': {'thread_id': thread_id}},
#         stream_mode='values'
#     )
#     for event in events:
#         event['messages'][-1].pretty_print()

#     # add human feedback
#     human_response = "你可以参考 langgraph 这个库，它可以帮助你快速构建 AI Agent 系统"
#     human_command = Command(resume={"data": human_response})
#     events = graph.stream(
#         human_command,
#         {'configurable': {'thread_id': thread_id}},
#         stream_mode='values'
#     )
#     for event in events:
#         event['messages'][-1].pretty_print()