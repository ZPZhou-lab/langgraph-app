from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

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

async def mock_agent_streaming_response(message: str):
    """mock agent response, simulating output token streaming"""
    response = f"echo: {message}"
    for r in response:
        await asyncio.sleep(0.05)  # simulate delay
        yield r

@app.post("/chat/stream")
async def chat_stream(user_message: UserMessage):
    async def event_generator():
        async for token in mock_agent_streaming_response(user_message.message):
            # SSE event
            yield f'data: {json.dumps({"token": token})}\n\n'
        yield 'data: {"end": true}\n\n'
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)