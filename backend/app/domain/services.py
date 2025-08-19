from .models import IsInit
from fastapi import Depends
from app.schemas.chat import Chat, Message, Prompt
from app.infrastructure.ollama.ollama_client import is_ollama_running, start_ollama, list_ollama_models,generate_llm_response
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.database.db_models import Chat, Base,Message
from app.infrastructure.database.crud import add_chat, get_chat, update_chat, delete_chat,add_message

DATABASE_URL = "postgresql://nikilps:Admin123@localhost:6969/wingman_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Global chats dictionary to persist for server lifetime
chats = {}  # Dict[str, Chat]
chat_cache = () #Tuple[str,Chat]

# Dependency for session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UtilServices:       
    def __init__(self):
        pass

    def build_context_from_history(chat: Chat)->str:

        formatted_messages = []

        for msg in chat.messages:
            role_label = "User" if msg.role == "user" else "Assistant"
            timestamp_str = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted_messages.append(f"[{timestamp_str}] {role_label}: {msg.content.strip()}")
        
        return "\n".join(formatted_messages)


class ChatService:
    def __init__(self):
        pass

    def create_chat(self, userPrompt='', db: Session = Depends(get_db) )->str:
        global chat_cache
        chat_id = str(uuid.uuid4())
        if userPrompt:
            chat_name = f"New Chat: {userPrompt[:6]}"
            chat_summary = userPrompt[:12]
        else:
            chat_name = "New Chat"
            chat_summary = 'No Messages!!!!'

        created_at = datetime.now()
        updated_at = datetime.now()
        chat = Chat(
            chatId=chat_id,
            chatName=chat_name,
            chatSummary=chat_summary,
            messages=[],
            createdAt=created_at,
            updatedAt=updated_at
        )
        # Adding to database
        try:
            new_chat = Chat(**chat)
            add_chat(db,new_chat)
        except Exception as e:
            print('There was an error adding chat to database',e)

        # This is to cache the chats so you dont have to retrieve the chat from the database every time
        chat_cache = (chat_id,chat)
        print('the chat cache in create_chat is',chat_cache)
        chats[chat_id] = chat
        return chat_id
    
    def get_chat_byID(self, chatId, db: Session = Depends(get_db))->Chat:
        global chat_cache
        """ Retrieve chat by ID if given else raise error """
        
        # if chatId in chats:
        #     #store in cache
        #     chat_cache = (chatId,chats[chatId])
        #     print('the chat cache in get_chat_byID is ',chat_cache)
            
        #     return chats[chatId]
        # else:
        #     raise ValueError(f"Chat with ID {chatId} does not exist.")
        try:
            if chat_cache[0] == chatId:
                return chat_cache[1]
            # get chat from database and update the cache
            chat = get_chat(db, chatId)
            return chat
        except Exception as e:
            print(f'there was an error retrieving chat with the ID {chatId}')
            raise ValueError(f"Chat with ID {chatId} does not exist.")
    
    def get_all_chats(self,db: Session = Depends(get_db)):
        """
        Return all chats as list of dicts (serialized for frontend)
        TODO: add pagination and sorting
        """
        print('the chat cache in get_all_chats is',chat_cache)
        # print(f'all list values are {chats}')
        return [chat.model_dump() for chat in chats.values()]
    
    """ TODO: The adding of messages can be consolidated into a single method if needed """

    def add_user_message(self, chatId, prompt:Prompt,db: Session = Depends(get_db)):
        global chat_cache
        print('the chat cache in add_user_message is ',chat_cache)
        # remove the magic numbers
        if chat_cache and chat_cache[0] == chatId:
            print('got data from chat cache')
            chat = chat_cache[1]
        else:
            print('had to search for data :(')
            chat = self.get_chat_byID(chatId) #remove, to get from database

        try:
            context = UtilServices.build_context_from_history(chat)
            # Add user prompt
            user_msg = Message(id=str(uuid.uuid4()), content=prompt.message, role='user', timestamp=datetime.now())
            chat.messages.append(user_msg)
            new_user_message = Message(**user_msg)
            _ = add_message(db, new_user_message)
            chat.updatedAt = user_msg.timestamp
            if not prompt.model:
                raise "There is no LLM selected"
            
            print('the context for the chat is',context)
            # Generate response and add to chat
            llm_reply = generate_llm_response(prompt.message, prompt.model, context) #TODO: create a function to create context from messages
            assistant_msg = Message(id=str(uuid.uuid4()), content=llm_reply, role='assistant', timestamp=datetime.now())
            print(f"Generated response: {llm_reply}")
            chat.messages.append(assistant_msg)
            new_llm_message = Message(**assistant_msg)
            _ = add_message(db, new_llm_message)
            chat.updatedAt = user_msg.timestamp


            # update the cache
            print('Updated the cache')
            chat_cache = (chatId,chat)

            chats[chatId] = chat
            return assistant_msg
        except Exception as e:
            print("There was an error in adding the user message",e)
            raise e
        
    @DeprecationWarning
    def add_assistant_message(self, chatId, content:Prompt):
        global chat_cache
        if chat_cache and chat_cache[0] == chatId:
            print('got data from chat cache')            
            chat = chat_cache[1]
        else:
            print('had to search for data :(')
            chat = self.get_chat_byID(chatId) #remove, to get from database
        
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now()
        try:
            msg = Message(id=msg_id, content=content.message, role='assistant', timestamp=timestamp)
            chat.messages.append(msg)
            chat.updatedAt = msg.timestamp
            # update the cache
            chat_cache = (chatId,chat)
            chats[chatId] = chat
            return True
        except Exception as e:
            print("There was an error in adding the LLM message")
            raise e

    def get_chat_history(self, chatId):
        global chat_cache
        if chat_cache and chat_cache[0] == chatId:
            print('got data from chat cache')
            chat = chat_cache[1]
        else:
            print('had to search for data :(')
            chat = self.get_chat_byID(chatId) #remove, to get from database
        return chat.messages
    
    def update_chat_meta_data(self,chatId,userPrompt):
        global chat_cache
        print('the chat cache in update_chat_meta_data is',chat_cache)
        try:
            if chat_cache and chat_cache[0] == chatId:
                print('got data from chat cache')
                chat = chat_cache[1]
            else:
                print('had to search for data :(')
                chat = self.get_chat_byID(chatId) #remove, to get from database

            chat_name = f"New Chat: {userPrompt[:6]}"
            chat_summary = userPrompt[:12]
            updated_at = datetime.now()

            # update chat
            chat.chatName = chat_name
            chat.chatSummary = chat_summary
            chat.updatedAt = updated_at

            if chat_cache[0] == chatId:
                print('Updated the cache')
                chat_cache = (chatId,chat)
            # update the cache
            updated_chat = Chat(**chat)
            _ = update_chat(db,updated_chat)
            chats[chatId] = chat
            return True

        except Exception as e:
            print(f'There was an error in updating the chat',e)
            raise e



    
class IsInitService:
    def __init__(self):
        # Start with isInit set to False
        self.is_init = False

    def update_init(self, status: bool):
        self.is_init = status
        return IsInit(is_init=self.is_init)


    def check_init(self):

        if not is_ollama_running():
            try:
                start_ollama()
                self.update_init(self, status=True)
                return self.is_init
            except Exception as e:
                print(f"❌ Error starting Ollama: {e}")
                self.update_init(self, status=False)
                return e


        else:
            list_ollama_models()

        return IsInit(is_init=self.is_init)
    


    
