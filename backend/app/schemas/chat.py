from pydantic import BaseModel
from datetime import datetime
from typing import List

class Message(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime

class Chat(BaseModel):
    chatId: str
    chatName: str
    messages: List[Message]
    createdAt: datetime
    updatedAt: datetime

class ChatRequest(BaseModel):
    chatId: str
    prompt: str

class ChatResponse(BaseModel):
    message: Message
    chatId: str


