from .models import IsInit
from app.schemas.chat import Chat, Message, Prompt
from app.infrastructure.ollama_client import is_ollama_running, start_ollama, list_ollama_models,generate_llm_response
import uuid
from datetime import datetime


import uuid
from datetime import datetime



# Global chats dictionary to persist for server lifetime
chats = {}  # Dict[str, Chat]

class ChatService:
    def __init__(self):
        pass

    def create_chat(self, userPrompt='')->str:
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
        # This is to cache the chats so you dont have to retrieve the chat from the database every time
        chats[chat_id] = chat
        return chat_id
    
    def get_chat_byID(self, chatId)->Chat:
        """ Retrieve chat by ID if given else raise error """
        if chatId in chats:
            return chats[chatId]
        else:
            raise ValueError(f"Chat with ID {chatId} does not exist.")
    
    def get_all_chats(self):
        """
        Return all chats as list of dicts (serialized for frontend)
        TODO: add pagination and sorting
        """
        # print(f'all list values are {chats}')
        return [chat.model_dump() for chat in chats.values()]
    
    """ TODO: The adding of messages can be consolidated into a single method if needed """

    def add_user_message(self, chatId, prompt:Prompt):
        chat = self.get_chat_byID(chatId)
        try:
            # Add user prompt
            user_msg = Message(id=str(uuid.uuid4()), content=prompt.message, role='user', timestamp=datetime.now())
            chat.messages.append(user_msg)
            chat.updatedAt = user_msg.timestamp
            if not prompt.model:
                raise "There is no LLM selected"
            # Generate response and add to chat
            llm_reply = generate_llm_response(prompt.message, prompt.model) #TODO: create a function to create context from messages
            assistant_msg = Message(id=str(uuid.uuid4()), content=llm_reply, role='assistant', timestamp=datetime.now())
            print(f"Generated response: {llm_reply}")
            chat.messages.append(assistant_msg)
            chat.updatedAt = user_msg.timestamp


            # update the cache
            chats[chatId] = chat
            return assistant_msg
        except Exception as e:
            print("There was an error in adding the user message",e)
            raise e
        
    @DeprecationWarning
    def add_assistant_message(self, chatId, content:Prompt):
        chat = self.get_chat_byID(chatId)
        msg_id = str(uuid.uuid4())
        timestamp = datetime.now()
        try:
            msg = Message(id=msg_id, content=content.message, role='assistant', timestamp=timestamp)
            chat.messages.append(msg)
            chat.updatedAt = msg.timestamp
            # update the cache
            chats[chatId] = chat
            return True
        except Exception as e:
            print("There was an error in adding the LLM message")
            raise e

    def get_chat_history(self, chatId):
        chat = self.get_chat_byID(chatId)
        return chat.messages
    
    def update_chat_meta_data(self,chatId,userPrompt):

        try:
            chat = self.get_chat_byID(chatId)

            chat_name = f"New Chat: {userPrompt[:6]}"
            chat_summary = userPrompt[:12]
            updated_at = datetime.now()

            # update chat
            chat.chatName = chat_name
            chat.chatSummary = chat_summary
            chat.updatedAt = updated_at

            # update the cache
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
    
