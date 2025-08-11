""" TODO rename the file as this endpoint should be for handling chat messages and should be agnostic to any route """

from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, Message,Chat
from app.domain.services import ChatService
from app.infrastructure.ollama_client import generate_llm_response,list_ollama_models
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
    chat_service.create_chat(chat_id,chat_name)
    # Since the chat is created, there is going to be one message at maximum
    if payload.messages:
        llms = list_ollama_models()
        llm_reply = generate_llm_response(payload.messages[0], llms[0] if llms else '')
        chat_service.add_user_message(chat_id, payload.messages[0])
        print(f"Generated response: {llm_reply}")
        chat_service.add_assistant_message(chat_id, llm_reply)

    # Need to add error handling whe using database
    get_chat = chat_service.get_chat_byID(chat_id)
    print(f"Chat created with ID: {get_chat.chatId}, Name: {get_chat.chatName}, Messages: {len(get_chat.messages)}")
    return True

@router.get("/get_chat/{chatId}", response_model=ChatResponse)
def get_chat(chatId: str):
    print(f"Retrieving all chats : {chat_service.get_all_chats()}")
    try:
        chat = chat_service.get_chat_byID(chatId)
        return ChatResponse(message=chat.messages[-1] if chat.messages else None, chatId=chat.chatId)
    except ValueError as e:
        print(f"Error retrieving chat: {e}")
        raise HTTPException(status_code=404, detail=str(e))
