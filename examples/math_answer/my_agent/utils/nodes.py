from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import END
from my_agent.utils.state import State
from my_agent.utils.tools import CodeInterpreter, evaluate_answer

tools_list = [CodeInterpreter(), evaluate_answer]
tools = ToolNode(tools=tools_list)

def route_tools(state: State):
    """
    Use this in conditional edges to route the ToolNode
    """

    messages = state.get('messages', [])
    if messages:
        tool_message = messages[-1]
        if hasattr(tool_message, 'tool_calls') and len(tool_message.tool_calls) > 0:
            return "tools"
        return END
    else:
        raise ValueError("No messages found in state")


def chatbot(state: State):
    """
    a simple chatbot function that uses the ChatOllama model to respond to messages.
    """
    # create a ChatOllama instance
    llm = ChatOllama(model='qwen3:8b', reasoning=False)
    llm = llm.bind_tools(tools=tools_list)
    message = llm.invoke(state["messages"])
    # disable parallel tool calls so as to use human_assistance interrupt
    assert len(message.tool_calls) <= 1
    return {"messages": [message], }