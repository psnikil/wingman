***

# Wingman Backend (FastAPI + Ollama + PostgreSQL)

Welcome to the backend of the Wingman LLM Chat App! This backend provides a robust, extensible API for chatting with a locally running LLM via Ollama, with PostgreSQL for persistent chat storage, following Clean Architecture principles for maintainability and scalability.

## Table of Contents
- [Project Overview](#project-overview)
- [Architecture Structure](#architecture-structure)
- [Setup & Installation](#setup--installation)
- [Database Setup](#database-setup)
- [Key Dependencies](#key-dependencies)
- [Ollama LLM Integration](#ollama-llm-integration)
- [Database Models](#database-models)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Extending & Contributing](#extending--contributing)
- [Future Roadmap](#future-roadmap)

***

## Project Overview

The backend powers a local ChatGPT-like experience, enabling chat with LLMs (e.g., Llama3) running on your machine via Ollama. It now includes **PostgreSQL integration** for persistent chat storage and is designed for easy extension (RAG, agents, advanced DB features, etc.) and seamless integration with the Next.js frontend.

***

## Architecture Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── api/                    # HTTP API routers
│   │   └── v1/                 # API version 1
│   ├── domain/                 # Business logic entities, services
│   ├── infrastructure/         # Integrations (ollama, database)
│   │   ├── ollama/             # Ollama client
│   │   └── database/           # Database models and CRUD
│   └── schemas/                # Pydantic models for API
├── database/                   # Database related files
│   ├── __init__.py
│   ├── db_models.py               # SQLAlchemy models (Chat, Message)
│   ├── crud.py                 # Database CRUD operations
│   ├── connection.py           # Database connection setup
│   └── init_db.py              # Database initialization script
├── utils/                      # Helpers/utilities
├── requirements.txt            # Python dependencies
├── migrations/                 # Future DB migrations (Alembic)
├── tests/                      # Unit/integration tests
├── .env.example                # Example environment config
└── README.md                   # This file
```

***

## Setup & Installation

### 1. Clone the repository
```sh
git clone 
cd backend
```

### 2. Create and activate a virtual environment
```sh
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
- Install PostgreSQL locally or use a cloud instance
- Create a database for your project
- Update your database credentials in `.env` file

### 5. Install & start Ollama
- Download from [Ollama](https://ollama.ai)
- Pull a model (e.g., llama3):
```sh
ollama pull llama3
ollama serve
```
- Ollama runs at `http://localhost:11434`

### 6. Initialize the database
```sh
python database/init_db.py
```

### 7. Run the backend server
```sh
uvicorn app.main:app --reload
```

The API is now live at `http://localhost:8000`

***

## Database Setup

### Environment Configuration
Create a `.env` file with your database credentials:
```env
DATABASE_URL=postgresql://yourusername:yourpassword@localhost/yourdatabase
```

### Database Models
The application uses two main models:

**Chat Model:**
- `chatId` (String, Primary Key)
- `chatName` (String)
- `chatSummary` (String)
- `last_updated` (DateTime)
- `created_at` (DateTime)
- `messages` (Relationship to Message)

**Message Model:**
- `messageId` (String, Primary Key)
- `chatId` (String, Foreign Key)
- `role` (Enum: 'user' | 'assistant')
- `content` (String)
- `timestamp` (DateTime)

### Database Operations
Available CRUD operations:
- **add_chat**: Create new chat with messages
- **get_chat**: Retrieve chat by ID with all messages
- **update_chat**: Modify chat properties
- **delete_chat**: Remove chat and all associated messages
- **get_allchats**: Get all chats
- **add_message**: Add message to a given chat_id
- **get_messages**: Get messages for a given chat_id


***

## Key Dependencies

- **FastAPI**: Web API framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database (asyncpg/psycopg2-binary drivers)
- **Ollama**: Local LLM integration
- **Pydantic**: Data validation
- **langchain**: (optional) RAG/agents
- **faiss-cpu**: (optional) Vector search
- **pytest**: Testing framework

See `requirements.txt` for the full list.

***

## Ollama LLM Integration

- **Integration**: `app/infrastructure/ollama/client.py`
- **Connection**: REST API to Ollama at `localhost:11434`
- **Models**: Use any model pulled locally (e.g., llama3, mistral)

***

## API Reference

| Route                | Method | Description                                  |
|----------------------|--------|----------------------------------------------|
| `/CreateChat`                   | POST   | Send user message, create chat    |
| `/get_chat_messages/{chatId}`   | GET    | Fetch single chat by ID           |
| `/response`                     | POST   | Get response from LLM             |
| `/updatechat`                   | POST   | Update chat meta data             |
| `/is_init`                      | GET    | Health check for ollama           |
| `/db_startup`                   | GET    | Health check for postgreSQL db    |

### Example: Send user message to chat
**Request:**
```json
{
  "prompt": "Hello, how are you?"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thanks for asking!"
}
```

***

## Database Models & Schemas

Defined in `database/db_models.py` (SQLAlchemy) and `app/schemas/` (Pydantic):

```python
# SQLAlchemy Models
class Chat_db(Base):
    chatId: str
    chatName: str
    chatSummary: str
    created_at: datetime
    updatedAt: datetime

class Message_db(Base):
    messageId: str
    role: Enum['user', 'assistant']
    chatId:str
    content: str
    timestamp: datetime
```

```python
# Pydantic Schemas
class Message(BaseModel):
    messageId: str = ""
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime

class Chat(BaseModel):
    chatId: str
    chatName: str
    chatSummary:str
    messages: List[Message]
    createdAt: datetime
    updatedAt: datetime

class CreateChatRequest(BaseModel):
    userPrompt: str = ""
    model:str = ''

class ChatRequest(BaseModel):
    chatId: str
    prompt: str
    model: str = ''  # Optional, can be used to specify which LLM to use

class ChatResponse(BaseModel):
    chatId: str #not sure we need to send back chatID in response
    message: Message

#This is the type when request a new chat window
class ChatDataResponse(BaseModel):
    chatId: str
    messages: List[Message] = []
    

class Prompt(BaseModel):
    message:str
    model:str

class UpdateChat(BaseModel):
    chatId:str
    prompt:str
```

***

## Testing

- Tests are in `tests/` and mirror the app structure
- Run all tests:
```sh
pytest
```

***

## Extending & Contributing

### Adding Features
- **Add endpoints**: Create routers in `app/api/v1/`, update schemas as needed
- **Business logic**: Extend in `app/domain/`
- **Integrations**: Add new clients in `app/infrastructure/` (e.g., vector search)
- **Database**: Extend models in `database/models.py`, add CRUD in `database/crud.py`
- **Versioning**: Future APIs go under `app/api/v2/`, etc.

### Database Migrations
For schema changes, use Alembic:
```sh
# Generate migration
alembic revision --autogenerate -m "Add new column"
# Apply migration
alembic upgrade head
```

PRs and issues welcome!

***

## Future Roadmap

- **✅ PostgreSQL**: Store chat/message history with SQLAlchemy *(Completed)*
- **RAG/Agents**: Add vector search and agent orchestration
- **Alembic Migrations**: Database schema versioning
- **Dockerization**: Containerize for easy deployment
- **API Versioning**: Support breaking changes via `/api/v2/`, etc.
- **User Authentication**: Multi-user support
- **WebSocket Support**: Real-time chat updates

***

For questions, contact the dev team. Happy coding! 🚀

