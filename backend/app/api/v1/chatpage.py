""" TODO rename the file as this endpoint should be for handling chat messages and should be agnostic to any route """

from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Message,Chat
from app.domain.services import ChatService
from app.infrastructure.ollama_client import generate_llm_response
import uuid
from datetime import datetime

router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
def send_message(payload: ChatRequest):

    print(f"Received chat request: {payload}")
    # Add user message to history
    user_msg = chat_service.add_user_message(payload.chatId, payload.prompt)
    # Send prompt to LLM
    llm_reply = generate_llm_response(payload.prompt)
    # Add assistant message to history
    assistant_msg = chat_service.add_assistant_message(payload.chatId, llm_reply)
    print(f"Generated response: {assistant_msg}")
    return ChatResponse(message=assistant_msg, chatId=payload.chatId)

@router.post("/Createchat", response_model=bool)
def create_chat(payload: Chat):
    print(f"Received chat request: {payload}")
    chat_id = payload.chatId
    chat_name = payload.chatName
    created_at = payload.createdAt or datetime.now()
    updated_at = payload.updatedAt or datetime.now()
    chat_service.get_or_create_chat(chat_id,chat_name)
    # Since the chat is created, there is going to be one message at maximum
    if payload.messages:
        chat_service.add_user_message(chat_id, payload.messages[0].content)

    # Need to add error handling whe using database
    return True
