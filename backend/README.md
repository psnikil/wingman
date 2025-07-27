# Backend README

Welcome to the backend of the Wingman LLM Chat App! This document provides an in-depth guide for developers covering project structure, infrastructure, data types, API routes, setup instructions, and tips for future growth.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Setup & Installation](#setup--installation)
- [Infrastructure](#infrastructure)
  - [Dependencies](#dependencies)
  - [Ollama/LLM Integration](#ollamallm-integration)
  - [Database Integration (Future: PostgreSQL)](#database-integration-future-postgresql)
- [Data Types & Schemas](#data-types--schemas)
- [API Routes](#api-routes)
- [Testing](#testing)
- [Extending & Contributing](#extending--contributing)
- [Tips for Future Additions](#tips-for-future-additions)
- [Project Maintainers](#project-maintainers)

## Project Architecture

The backend follows **Clean Architecture** principles for separation of concerns, modularity, and scalability:

```
backend/
├── app/
│   ├── main.py             # FastAPI entrypoint
│   ├── api/                # HTTP API (routers, v1/, schemas)
│   ├── core/               # App config, error handling, settings
│   ├── domain/             # Pure business logic (entities, services, interfaces)
│   ├── infrastructure/     # Integrations: ollama, postgres, vector DBs, etc.
│   ├── schemas/            # Pydantic models for request/response
│   └── utils/              # Helpers and shared utilities
├── tests/                  # Unit, integration, e2e tests
├── migrations/             # Alembic DB migrations (PostgreSQL)
├── requirements.txt        # Python dependencies
├── Dockerfile
├── .env.example
└── README.md
```

## Setup & Installation

1. **Clone the repository**:

   ```sh
   git clone 
   cd backend
   ```

2. **Python Environment**:

   ```sh
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Install & Start Ollama**:

   - Download and install [Ollama](https://ollama.com/) for your OS.
   - Pull an LLM model:
     ```sh
     ollama pull llama3
     ```
   - Serve Ollama (runs on `http://localhost:11434`):
     ```sh
     ollama serve
     ```

5. **Run the Backend Server**:

   ```sh
   uvicorn app.main:app --reload
   ```

   The API is now live at `http://localhost:8000/`.

## Infrastructure

### Dependencies

Essential dependencies (production-quality):

- `fastapi` (web API)
- `uvicorn` (ASGI server)
- `ollama` (local LLM SDK)
- `pydantic` (data validation)
- `langchain`, `llama-index` (optional: RAG)
- `faiss-cpu` (optional: semantic/vector search for RAG)
- `sqlalchemy`, `asyncpg` (PostgreSQL, for future)
- `alembic` (migrations)
- `pytest` (testing)

See `requirements.txt` for the full list.

### Ollama/LLM Integration

- **Integration Layer**: `infrastructure/ollama_client.py`
- **Connection**: Via Ollama SDK or raw REST HTTP to `localhost:11434`.
- **Models**: Use `llama3`, `mistral`, or any model pulled locally.

### Database Integration (Future: PostgreSQL)

- **Connection**: Managed in `infrastructure/postgres/`.
- **ORM**: Use SQLAlchemy; config in `core/config.py`.
- **Repo Pattern**: Abstract interfaces in `domain/repositories.py`, concrete implementations in `infrastructure/postgres/repository.py`.
- **Migrations**: Handled with Alembic in `migrations/`.

## Data Types & Schemas

**API and Business Layer Types (Pydantic & Domain Models):**

```python
# app/schemas/chat.py
from pydantic import BaseModel
from datetime import datetime

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

- **Request/Response models** for each endpoint live in `app/schemas/`.
- **Business logic models** in `app/domain/`.
- **DB models** (future) under `infrastructure/postgres/`.

## API Routes

| Route                | Method | Description                                  | Input Schema   | Output Schema         |
|----------------------|--------|----------------------------------------------|---------------|----------------------|
| `/chat`              | POST   | Send user message, get LLM response          | `ChatRequest`  | `ChatResponse`       |
| `/chats/{chat_id}`   | GET    | Fetch single chat by ID                      | —             | `Chat` (full object) |
| `/chats`             | GET    | List all user chats (future: from db)        | —             | `List[Chat]`         |
| `/chats`             | POST   | Create a new chat session                    | `ChatCreate`   | `Chat`               |
| `/health`            | GET    | Health check endpoint                        | —              | status string        |

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

## Testing

- **Unit and integration tests** reside in `tests/` and mirror app structure.
- Run tests with:
  ```sh
  pytest
  ```

## Extending & Contributing

- **New Endpoints**: Add routes in `app/api/v1/` and update schemas.
- **New Business Logic**: Extend domain models/services (`app/domain/`).
- **LLM/Vector DBs**: Place integrations under `infrastructure/`.
- **Database Models**: Keep ORM-specific code out of domain; add/extend in infrastructure and schema layers.
- **Versioning**: Future APIs go under `api/v2/` etc.

## Tips for Future Additions

- **PostgreSQL**:
  - Define interface in `domain/repositories.py`, implement in `infrastructure/postgres/`.
  - Store chat/message history.
  - Manage migrations with Alembic.
- **RAG/Agents**:
  - Add vector search logic in `infrastructure/`.
  - Keep orchestration and agent workflows in business/domain layer.
- **API Versioning**: Organize by `api/v1/`, `api/v2/` to support breaking changes.
- **Dockerization**: Use `Dockerfile` and `.env` for containerized deployments.

## Project Maintainers

For questions, please contact the dev team.

**Happy coding! This backend is designed for long-term maintainability, LLM extensibility, and rapid integration with more advanced AI and storage infrastructure.**

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/63572251/17b777a0-2cd2-470f-8463-abbdd87c9836/README.md