from .chats_api import router as chat_router
from .inits_api import router as inits_router
from .ollama_api import router as ollama_router

__all__ = ["chat_router","inits_router","ollama_router"]