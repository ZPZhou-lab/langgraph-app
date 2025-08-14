from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from chatbot.my_agent.agent import root_graph

app = FastAPI(title="Chatbot", version="0.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserMessage(BaseModel):
    message: str

class AgentResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=AgentResponse)
async def chat(user_message: UserMessage):
    return AgentResponse(response=f"echo: {user_message.message}")


def agent_streaming_response(message: str):
    """streaming response from the agent"""
    events = root_graph.stream(
        input={'messages': [{'role': 'user', 'content': message}]},
        config={'configurable': {'thread_id': '1'}},
        stream_mode='messages'
    )
    for event in events:
        msg, _ = event
        token = msg.content
        yield token

@app.post("/chat/stream")
async def chat_stream(user_message: UserMessage):
    async def event_generator():
        for token in agent_streaming_response(user_message.message):
            # SSE event
            yield f'data: {json.dumps({"token": token})}\n\n'
        yield 'data: {"end": true}\n\n'
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)