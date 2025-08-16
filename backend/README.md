---
# Wingman Backend (FastAPI + Ollama)

Welcome to the backend of the **Wingman LLM Chat App**! This backend provides a robust, extensible API for chatting with a locally running LLM (via Ollama), following Clean Architecture principles for maintainability and scalability.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture & Structure](#architecture--structure)
- [Setup & Installation](#setup--installation)
- [Key Dependencies](#key-dependencies)
- [Ollama/LLM Integration](#ollamallm-integration)
- [API Reference](#api-reference)
- [Data Models & Schemas](#data-models--schemas)
- [Testing](#testing)
- [Extending & Contributing](#extending--contributing)
- [Future Roadmap](#future-roadmap)

---

## Project Overview

The backend powers a local ChatGPT-like experience, enabling chat with LLMs (e.g., Llama3) running on your machine via [Ollama](https://ollama.com/). It is designed for easy extension (RAG, agents, DB, etc.) and seamless integration with the Next.js frontend.

## Architecture & Structure

Follows Clean Architecture for clear separation of concerns:

```
backend/
├── app/
│   ├── main.py             # FastAPI entrypoint
│   ├── api/                # HTTP API (routers, v1/)
│   ├── domain/             # Business logic (entities, services)
│   ├── infrastructure/     # Integrations: ollama, (future: DB, vector search)
│   ├── schemas/            # Pydantic models for API
│   └── utils/              # Helpers/utilities
├── requirements.txt        # Python dependencies
├── migrations/             # (Future) DB migrations
├── tests/                  # Unit/integration tests
├── .env.example            # Example environment config
└── README.md               # This file
```

## Setup & Installation

1. **Clone the repository**
  ```sh
  git clone <repo-url>
  cd backend
  ```
2. **Create and activate a virtual environment**
  ```sh
  python -m venv venv
  # On Windows:
  venv\Scripts\activate
  # On macOS/Linux:
  source venv/bin/activate
  ```
3. **Install dependencies**
  ```sh
  pip install -r requirements.txt
  ```
4. **Install & start Ollama**
  - Download from [Ollama](https://ollama.com/)
  - Pull a model (e.g., llama3):
    ```sh
    ollama pull llama3
    ollama serve
    ```
  - Ollama runs at `http://localhost:11434`
5. **Run the backend server**
  ```sh
  uvicorn app.main:app --reload
  ```
  The API is now live at [http://localhost:8000](http://localhost:8000)

## Key Dependencies

- [FastAPI](https://fastapi.tiangolo.com/) (web API)
- [Uvicorn](https://www.uvicorn.org/) (ASGI server)
- [Ollama](https://ollama.com/) (local LLM)
- [Pydantic](https://docs.pydantic.dev/) (data validation)
- [langchain](https://python.langchain.com/) (optional: RAG/agents)
- [faiss-cpu](https://github.com/facebookresearch/faiss) (optional: vector search)
- [pytest](https://docs.pytest.org/) (testing)

See `requirements.txt` for the full list.

## Ollama/LLM Integration

- **Integration**: `app/infrastructure/ollama_client.py`
- **Connection**: REST API to Ollama at `localhost:11434`
- **Models**: Use any model pulled locally (e.g., llama3, mistral)

## API Reference

| Route                | Method | Description                                  |
|----------------------|--------|----------------------------------------------|
| `/chat`              | POST   | Send user message, get LLM response          |
| `/chats/{chat_id}`   | GET    | Fetch single chat by ID                      |
| `/chats`             | GET    | List all user chats (future: from db)        |
| `/chats`             | POST   | Create a new chat session                    |
| `/health`            | GET    | Health check endpoint                        |

**Example: Send user message to /chat**

Request:
```json
{
  "prompt": "Hello, how are you?"
}
```
Response:
```json
{
  "response": "I'm doing well, thanks for asking!"
}
```

## Data Models & Schemas

Defined in `app/schemas/` (Pydantic):

```python
class Message(BaseModel):
   id: str
   content: str
   role: str  # 'user' or 'assistant'
   timestamp: datetime
   isLoading: bool = False

class Chat(BaseModel):
   chatId: str
   chatName: str
   chatSummary: str
   messages: list[Message]
   createdAt: datetime
   updatedAt: datetime
```

## Testing

- Tests are in `tests/` and mirror the app structure
- Run all tests:
  ```sh
  pytest
  ```

## Extending & Contributing

- **Add endpoints**: Create routers in `app/api/v1/`, update schemas as needed
- **Business logic**: Extend in `app/domain/`
- **Integrations**: Add new clients in `app/infrastructure/` (e.g., DB, vector search)
- **Versioning**: Future APIs go under `api/v2/`, etc.
- **PRs and issues welcome!**

## Future Roadmap

- **PostgreSQL**: Store chat/message history, use SQLAlchemy, Alembic for migrations
- **RAG/Agents**: Add vector search and agent orchestration
- **Dockerization**: Containerize for easy deployment
- **API Versioning**: Support breaking changes via `/api/v2/`, etc.

---

For questions, contact the dev team. Happy coding!