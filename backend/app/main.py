from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import inits_api
from app.api.v1 import chats_api
from app.api.v1 import ollama_api


origins = [
    "http://localhost:3000",  # Your Next.js app
    # Add more origins here if needed, e.g., your production domain
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allow these origins
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)
app.include_router(chats_api.router, prefix="/api/v1")
app.include_router(inits_api.router, prefix="/api/v1")
app.include_router(ollama_api.router, prefix="/api/v1")
