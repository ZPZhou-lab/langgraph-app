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
graph = builder.compile(checkpointer=None)


def print_snapshot(graph, config):
    print("=================================== Snapshot ===================================")
    snapshot = graph.get_state(config=config)
    print({k: v for k, v in snapshot.values.items() if k != "messages"})

    return snapshot

if __name__ == "__main__":
    # compile the graph using InMemorySaver
    memory = InMemorySaver()
    graph = builder.compile(checkpointer=memory)
    next_node = (START, )

    # while True:
    # get user input
    thread_id = "1"
    config = {'configurable': {'thread_id': thread_id}}

    mock_user_input = (
        "矩阵 [[1, 2], [3, 4]] 最大特征值是多少？当你确认答案后，使用 evaluate_answer 进行验证"
    )
    
    while len(next_node) > 0:
        user_input = input("Prompt: ")
        user_input = mock_user_input if user_input.strip() == "" else user_input.strip()

        if user_input.lower() == "exit":
            print("========== Bye ==========")
            break

        # run graph
        events = graph.stream(
            {'messages': [{'role': 'user', 'content': user_input}]},
            config, stream_mode='values'
        )
        for event in events:
            if "messages" in event:
                event['messages'][-1].pretty_print()
            
        snapshot = print_snapshot(graph, config)
        while len(snapshot.next) > 0:
            # add human feedback
            human_response = {
                "correct": input("确认回答是否正确？(y/n): ").strip().lower(),
                "correction": ""
            }
            if human_response['correct'].startswith('n'):
                human_response['correction'] = input("请提供修正答案: ").strip()
            human_command = Command(resume={
                "correct": human_response['correct'], 
                "correction": human_response.get('correction')
            })

            # run graph
            events = graph.stream(human_command, config, stream_mode='values')
            for event in events:
                if "messages" in event:
                    event['messages'][-1].pretty_print()
        
            # get snapshot
            snapshot = print_snapshot(graph, config)