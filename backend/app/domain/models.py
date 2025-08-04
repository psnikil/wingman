from typing import List
from datetime import datetime

class Message:
    def __init__(self, id, content, role, timestamp=None):
        self.id = id
        self.content = content
        self.role = role
        self.timestamp = timestamp or datetime.utcnow()

class Chat:
    def __init__(self, chatId, chatName, createdAt=None, updatedAt=None):
        self.chatId = chatId
        self.chatName = chatName
        self.createdAt = createdAt or datetime.utcnow()
        self.updatedAt = updatedAt or datetime.utcnow()
        self.messages: List[Message] = []

# This is the class for checking if the backend is initialized
class IsInit:
    def __init__(self, is_init: bool):
        self.is_init = is_init
