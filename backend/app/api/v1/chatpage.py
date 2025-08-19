""" TODO rename the file as this endpoint should be for handling chat messages and should be agnostic to any route """

from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, UpdateChat,Chat, ChatDataResponse,CreateChatRequest,Prompt
from app.domain.services import ChatService
from app.infrastructure.ollama.ollama_client import generate_llm_response,list_ollama_models


router = APIRouter()
chat_service = ChatService()



@DeprecationWarning
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

@router.post("/Createchat", response_model=str)
def create_chat(payload: CreateChatRequest):
    print(f"Received create chat request: {payload}")
    # get chat
    chat_id = chat_service.create_chat(payload.userPrompt)
    # Since the chat is created, there is going to be one message at maximum
    if payload.userPrompt:
        # TODO: model should be from the member of payload
        llms = list_ollama_models() #payload.model
        print(f"Available LLMs: {llms}")
        payload.llm = llms[0]
        prompt = Prompt(message=payload.userPrompt,model=payload.llm)

        llm_reply = chat_service.add_user_message(chat_id, prompt)

    # Need to add error handling whe using database
    # get_chat = chat_service.get_chat_byID(chat_id)
    # print(f"Chat created with ID: {get_chat.chatId}, Name: {get_chat.chatName}, Messages: {len(get_chat.messages)}")
    return chat_id

@router.get("/get_chat/{chatId}", response_model=ChatDataResponse)
def get_chat(chatId: str):
    # print(f"Retrieving all chats : {chat_service.get_all_chats()}")
    try:
        chat = chat_service.get_chat_byID(chatId)
        return ChatDataResponse(messages=chat.messages if chat.messages else [], chatId=chat.chatId)
    except ValueError as e:
        print(f"Error retrieving chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/get_all_chats", response_model=list) #TODO: change to list[Chat] when you know how to type caste
def get_all_chats():
    print(f"Retrieving all chats : {len(chat_service.get_all_chats())}")
    return chat_service.get_all_chats() 

@router.post("/response", response_model=ChatResponse)
def get_response(payload: ChatRequest):
    print(f"Received chat request: {payload}")

    try:

        llms = list_ollama_models()

        user_prompt = Prompt(message=payload.prompt, model=llms[0])
        # Add user message to history
        llm_reply = chat_service.add_user_message(payload.chatId, user_prompt)
    except Exception as e:
        print(f'There was an error in getting or generating the response',e)
        raise e
    
    print(f"Generated response: {llm_reply}")
    return ChatResponse(message=llm_reply, chatId=payload.chatId)


@router.post("/updatechat", response_model=bool)
def update_chat(payload:UpdateChat):
    # chat = chat_service.get_chat_byID(chatId)

    try:
        res = chat_service.update_chat_meta_data(payload.chatId,payload.prompt)
        return res
    except Exception as e:
        print(f'There was an error in updating the chat {e}')
        raise e

