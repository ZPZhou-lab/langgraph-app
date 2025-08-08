from pydantic import BaseModel, Field
from typing import Type, Any, Dict
from traceback import format_exc
from typing import Annotated
from langchain_core.tools import BaseTool, ToolException
from langchain_core.messages import ToolMessage
from langgraph.types import Command, interrupt
from langchain_core.tools import tool, InjectedToolCallId


@tool
def evaluate_answer(
    answer: str, 
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """
    To request the judger to evaluate whether the answer is correct.

    Parameters
    ----------
    answer : str
        The answer to be evaluated.
    """
    print("evaluate_answer is called")
    human_response = interrupt(
        {
            "question": "作答是否正确？",
            "answer": answer
        }
    )
    print("evaluate_answer interrupted continue")
    # If the answer is correct, return "Correct", otherwise make a correction.
    if human_response.get('correct', "").lower().startswith('y'):
        verified_answer = answer
        response = "Correct"
    else:
        verified_answer = human_response.get('correction', "")
        response = f"Make a correction: {verified_answer}"
    
    # update the graph state with a ToolMessage
    state_update = {
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
        "answer": verified_answer
    }
    return Command(update=state_update)


class CodeInterpreterInput(BaseModel):
    code: str = Field(description=
        "The python code to be executed.\n"
        "All the outputs needed to answer the question should be stored in a variable named `result`.\n"
        "- DO NOT use ``` to wrap the code block, code will be passed into `exec()` directly."
        "- Make sure `result` can be cast to a string."
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