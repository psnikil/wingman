"""
CRUD operation are written in this helper file
This file holds all the operation/functions performed on the database
"""

from sqlalchemy.orm import Session
from app.infrastructure.database.db_models import Chat,Message


# Add chat
def add_chat(session:Session,chat:Chat): #similar to create chat
    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat

def get_chat(session:Session,chat_id:str):
    return session.query(Chat).filter(Chat.chatId == chat_id).first()

def get_all_chats(session:Session):
    return session.query(Chat)

def update_chat(session:Session, chat_id:str, updates: dict):
    chat = get_chat(session,chat_id)
    for key,value in updates.items():
        setattr(chat,key,value)
    session.commit()
    return chat

def delete_chat(session:Session,chat_id:str):
    chat = get_chat(session,chat_id)
    session.delete(chat)
    session.commit()


def add_message(session:Session,message:Message):
    session.add(message)
    session.commit()
    session.refresh(message)

def get_message(session:Session,message_id:str):
    return session.query(Message).filter(Message.messageId == message_id).first()

def update_message(session:Session,message_id:str,updates: dict):
    message = get_message(session,message_id)
    for key,value in updates.items():
        setattr(message,key,value)
    session.commit()
    return message
