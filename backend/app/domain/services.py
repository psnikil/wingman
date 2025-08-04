from .models import Chat, Message, IsInit
from app.infrastructure.ollama_client import is_ollama_running, start_ollama, list_ollama_models
import uuid

class ChatService:
    def __init__(self):
        self.chats = {}  # Dict[str, Chat]

    def get_or_create_chat(self, chatId):
        if chatId not in self.chats:
            chat = Chat(chatId=chatId, chatName=f"Chat-{chatId[:4]}")
            self.chats[chatId] = chat
        return self.chats[chatId]

    def add_user_message(self, chatId, content):
        chat = self.get_or_create_chat(chatId)
        msg = Message(id=str(uuid.uuid4()), content=content, role='user')
        chat.messages.append(msg)
        chat.updatedAt = msg.timestamp
        return msg

    def add_assistant_message(self, chatId, content):
        chat = self.get_or_create_chat(chatId)
        msg = Message(id=str(uuid.uuid4()), content=content, role='assistant')
        chat.messages.append(msg)
        chat.updatedAt = msg.timestamp
        return msg

    def get_chat_history(self, chatId):
        chat = self.get_or_create_chat(chatId)
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
    
