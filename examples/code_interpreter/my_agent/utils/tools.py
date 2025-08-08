from pydantic import BaseModel, Field
from typing import Type, Any, Dict
from traceback import format_exc

from langchain_core.tools import BaseTool, ToolException
from langgraph.types import Command, interrupt
from langchain_core.tools import tool

@tool
def human_assistance(query: str) -> str:
    """
    Request assistance from a human expert to determine the next action.

    Parameters
    ----------
    query : str
        The questions asked for human assistance.
    """
    human_response = interrupt({"query": query})
    return human_response

class CodeInterpreterInput(BaseModel):
    code: str = Field(description=
        "The python code to be executed.\n"
        "All the outputs needed to answer the question should be stored in a variable named `result`.\n"
        "Make sure `result` can be cast to a string."
    )

class CodeInterpreter(BaseTool):
    """Tool that executes Python code and returns the result."""

    name: str = "code_interpreter"
    description: str = (
        "A code interpreter function to execute Python code and return the result."
        "You can use code_interpreter to do calculations to answer the question more accurately."
    )
    args_schema: Type[BaseModel] = CodeInterpreterInput
    handle_tool_error: bool = True
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def _run(self, code: str) -> Dict[str, Any]:
        try:
            result = code_interpreter(code)
        except Exception as e:
            error_message = (
                f"error when executing code: {code}.\n"
                f"catch Exception: {e}"
                f"\nTraceback:\n{format_exc()}"
            )
            raise ToolException(error_message)
        
        return {"result": result}
    

def code_interpreter(code: str) -> str:
    """
    executes the provided Python code and returns the result.

    Parameters
    ----------
    code : str
        The Python code to execute. It should define a variable named `result` which 
        contains all the output you needed. Make sure `result` is an object that can be converted to a string.
    """
    namespace = {} # Create a new namespace for code execution
    exec(code, namespace) # Execute the code in the isolated namespace
    # Return the result from the executed code
    return str(namespace.get('result', 'No variable named `result` found.'))