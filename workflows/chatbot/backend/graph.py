import sys
import os

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

from langchain_core.messages import HumanMessage, AIMessage
# add parent directory to path for importing agent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from my_agent.agent import graph


app = FastAPI(title="Chatbot API", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

# set templates
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求和响应模型
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class ConversationHistory(BaseModel):
    messages: List[dict]

# saves conversation history in memory
# should be replaced with a storage backend in production
conversations = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页，返回聊天界面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
async def root():
    """root path, returns API information"""
    return {"message": "Chatbot API is running", "version": "1.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage, conversation_id: str = "default"):
    """
    Chat with the LLM
    
    Args:
        chat_message: 
            The user's input message
        conversation_id: str
            The unique identifier for the conversation, default is "default"
    Returns:
        response: ChatResponse
            Contains the LLM's response and the conversation ID
    """
    try:
        if conversation_id not in conversations:
            conversations[conversation_id] = []

        # add user message
        user_message = HumanMessage(content=chat_message.message)
        conversations[conversation_id].append(user_message)
        
        # 准备输入状态
        input_state = {
            "messages": conversations[conversation_id]
        }
        
        # call the graph
        result = graph.invoke(
            input_state,
            config={"configurable": {"thread_id": conversation_id}},
            stream_mode='values'
        )
        
        # fetch llm response
        ai_response = result["messages"][-1]
        
        # update conversation history
        conversations[conversation_id] = result["messages"]
        
        return ChatResponse(
            response=ai_response.content,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")

@app.get("/conversations/{conversation_id}/history", response_model=ConversationHistory)
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history
    
    Args:
        conversation_id: str
            The unique identifier for the conversation
    Returns:
        message: ConversationHistory
            The list of messages in the conversation
    """
    if conversation_id not in conversations:
        return ConversationHistory(messages=[])
    
    messages = []
    for msg in conversations[conversation_id]:
        if isinstance(msg, HumanMessage):
            messages.append({"type": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"type": "ai", "content": msg.content})
    
    return ConversationHistory(messages=messages)

@app.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    clear a conversation by its unique conversation_id

    Args:
        conversation_id: str
            The unique identifier for the conversation
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"会话 {conversation_id} 已清除"}
    else:
        return {"message": f"会话 {conversation_id} 不存在"}

@app.get("/conversations")
async def list_conversations():
    """
    list all conversation in the memory
    """
    return {"conversations": list(conversations.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
