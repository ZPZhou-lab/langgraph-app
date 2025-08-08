from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import TypedDict, Annotated, Sequence

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    answer: str