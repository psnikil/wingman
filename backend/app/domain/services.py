from .models import Chat, Message, IsInit
from app.infrastructure.ollama_client import is_ollama_running, start_ollama, list_ollama_models
import uuid
from app.schemas.chat import Message
from datetime import datetime


# Global chats dictionary to persist for server lifetime
chats = {}  # Dict[str, Chat]

class ChatService:
    def __init__(self):
        pass

    def create_chat(self, chatId, chatName):
        if chatId not in chats:
            chat = Chat(chatId=chatId, chatName=chatName)
            chats[chatId] = chat
        return chats[chatId]
    
    def get_chat_byID(self, chatId):
        """ Retrieve chat by ID if given else raise error """
        if chatId in chats:
            return chats[chatId]
        else:
            raise ValueError(f"Chat with ID {chatId} does not exist.")
    
    def get_all_chats(self):
        """
        Return all chats
        TODO: add pagination and sorting
        """
        return list(chats.values())
    
    """ TODO: The adding of messages can be consolidated into a single method if needed """

    def add_user_message(self, chatId, message: Message):
        chat = self.get_chat_byID(chatId)
        msg = Message(id=message.id, content=message.content, role=message.role, timestamp=message.timestamp)
        chat.messages.append(msg)
        chat.updatedAt = msg.timestamp
        #this needs to be changes into the result of adding aka true or false
        #also this allows for error handling
        return msg

    def add_assistant_message(self, chatId, content):
        chat = self.get_chat_byID(chatId)
        msg = Message(id=str(uuid.uuid4()), content=content, role='assistant', timestamp=datetime.utcnow())
        chat.messages.append(msg)
        chat.updatedAt = msg.timestamp
        #this needs to be changes into the result of adding aka true or false
        #also this allows for error handling
        return msg

    def get_chat_history(self, chatId):
        chat = self.get_chat_byID(chatId)
        return chat.messages
    
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
    
