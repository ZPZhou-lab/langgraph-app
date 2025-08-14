from langgraph.graph import StateGraph, START, END
from chatbot.my_agent.utils.state import State
from chatbot.my_agent.utils.tools import chatbot
from langgraph.checkpoint.memory import InMemorySaver

# build a graph
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

# build graph
memory = InMemorySaver()
root_graph = builder.compile(checkpointer=memory)

# compile the graph
if __name__ == "__main__":
    memory = InMemorySaver()
    graph = builder.compile(checkpointer=memory)

    # get input message from user
    user_message = input("Prompt: ")
    # get the response from the chatbot
    events = graph.stream(
        input={'messages': [{'role': 'user', 'content': user_message}]},
        config={'configurable': {'thread_id': '1'}},
        stream_mode='messages'
    )
    for event in events:
        # print(event[0].content, end='', flush=True)
        event_msg, event_config = event
        token = event_msg.content
        if token:
            print(event_msg.content, end='', flush=True)
            # event['messages'][-1].pretty_print()
        else:
            print("\n", end='', flush=True)
    # get state from graph
    snapshot = graph.get_state(config={'configurable': {'thread_id': '1'}})
    print(snapshot.values)