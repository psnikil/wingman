from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Message
from app.domain.services import ChatService
from app.infrastructure.ollama_client import generate_llm_response
import uuid
from datetime import datetime

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
def send_message(payload: ChatRequest):
    # Add user message to history
    user_msg = chat_service.add_user_message(payload.chatId, payload.prompt)
    # Send prompt to LLM
    llm_reply = generate_llm_response(payload.prompt)
    # Add assistant message to history
    assistant_msg = chat_service.add_assistant_message(payload.chatId, llm_reply)
    return ChatResponse(message=assistant_msg, chatId=payload.chatId)
