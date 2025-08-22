""" TODO rename the file as this endpoint should be for handling chat messages and should be agnostic to any route """

from fastapi import APIRouter, HTTPException,Depends
from app.schemas.chat import ChatRequest, ChatResponse, UpdateChat,Chat, ChatDataResponse,CreateChatRequest,Prompt,Message
from app.domain.services import ChatService
from app.infrastructure.ollama.ollama_client import generate_llm_response,list_ollama_models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


DATABASE_URL = "postgresql://nikilps:Admin123@localhost:6969/wingman_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

router = APIRouter()
chat_service = ChatService()


# Dependency for session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@DeprecationWarning
@router.post("/chat", response_model=ChatResponse)
def send_message(payload: ChatRequest,db: Session = Depends(get_db)):

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
def create_chat(payload: CreateChatRequest, db: Session = Depends(get_db)):
    print(f"Received create chat request: {payload}")
    try:
        chat_id = chat_service.create_chat(db, payload.userPrompt)
        print(f'the created chat id is {chat_id}')
        # Since the chat is created, there is going to be one message at maximum
        if payload.userPrompt:
            # TODO: model should be from the member of payload
            # llms = list_ollama_models() #payload.model
            print(f"Available LLMs: {payload.model}")
            # payload.llm = llms[0]
            prompt = Prompt(message=payload.userPrompt,model=payload.model)

            llm_reply = chat_service.add_user_message(chat_id, prompt, db)
        return chat_id
    except Exception as e:
        print('there has been am error in creating the chat with error:',e)
        raise e


@router.get("/get_chat_messages/{chatId}", response_model=ChatDataResponse)
def get_chat(chatId: str, db: Session = Depends(get_db)):
    # print(f"Retrieving all chats : {chat_service.get_all_chats()}")
    print('The chat ID to get the data for is:',chatId)
    try:
        messages = chat_service.get_messages(chatId, db)
        # type casting to message type
        messages = [Message(**message.__dict__) for message in messages]
        return ChatDataResponse(messages=messages if messages else [], chatId=chatId)
    except ValueError as e:
        print(f"Error retrieving chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/get_all_chats", response_model=list[Chat]) #TODO: change to list[Chat] when you know how to type caste
def get_all_chats(db: Session = Depends(get_db)):
    try:
        all_chats = chat_service.get_all_chats(db)
        print(f"Retrieving all chats : {len(all_chats)}, {all_chats}")
        return all_chats
    except Exception as e:
        print(f'There was an error retrieving all chats with error: {e}')

@router.post("/response", response_model=ChatResponse)
def get_response(payload: ChatRequest, db: Session = Depends(get_db)):
    print(f"Received chat request: {payload}")

    try:

        # llms = list_ollama_models()

        user_prompt = Prompt(message=payload.prompt, model=payload.model)
        print('the llm in chats api is',payload)
        # Add user message to history
        llm_reply = chat_service.add_user_message(payload.chatId, user_prompt, db)
        print(f"Generated response: {llm_reply}")
        return ChatResponse(message=llm_reply, chatId=payload.chatId)

    except Exception as e:
        print(f'There was an error in getting or generating the response',e)
        raise e
    


@router.post("/updatechat", response_model=bool)
def update_chat(payload:UpdateChat, db: Session = Depends(get_db)):
    # chat = chat_service.get_chat_byID(chatId)

    try:
        res = chat_service.update_chat_meta_data(payload.chatId,payload.prompt, db)
        return res
    except Exception as e:
        print(f'There was an error in updating the chat {e}')
        raise e

