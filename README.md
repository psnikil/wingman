# Wingman: Local LLM Chat App (Full Stack)

Wingman is a full stack, locally running ChatGPT-like app that lets you chat with open-source LLMs (via Ollama) on your own machine. It features a modern custom UI, supports future RAG (Retrieval Augmented Generation), and is designed for privacy, extensibility, and developer friendliness.

---

## Features

- **Local LLM chat**: Interact with Llama3 or other models using Ollama
- **Modern UI**: Built with Next.js, TailwindCSS, and TypeScript
- **FastAPI backend**: Clean, modular Python backend
- **RAG-ready**: Designed for file indexing and retrieval-augmented generation
- **Extensible**: Add agents, new endpoints, or UI features easily
- **Containerizable**: Future Docker support for easy deployment

---

## Project Structure

```
WingMan/
├── backend/    # FastAPI app (Python, Ollama integration)
├── frontend/   # Next.js app (TypeScript, TailwindCSS)
└── README.md   # This file (global docs)
```

See each subfolder's README for detailed docs.

---

## Quick Start

### 1. Prerequisites

- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **Ollama** ([Download here](https://ollama.com/))

### 2. Clone the repository

```sh
git clone <repo-url>
cd WingMan
```

### 3. Backend Setup

```sh
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

#### Start Ollama and pull a model
```sh
ollama pull llama3
ollama serve
# Ollama runs at http://localhost:11434
```

#### Run the backend server
```sh
uvicorn app.main:app --reload
# API at http://localhost:8000
```

### 4. Frontend Setup

```sh
cd ../frontend
npm install
npm run dev
# App at http://localhost:3000
```

---

## Main Requirements

- **Ollama**: For running LLMs locally ([installation guide](https://ollama.com/))
- **Python 3.10+**: Backend (FastAPI, Pydantic, etc.)
- **Node.js 18+**: Frontend (Next.js, TailwindCSS)

---

## High-Level Architecture

- **Frontend**: Next.js app (TypeScript, TailwindCSS)
	- Modern, responsive UI
	- State managed with Zustand
	- Connects to backend via REST API
- **Backend**: FastAPI app (Python)
	- Handles chat, session, and LLM requests
	- Integrates with Ollama for LLM inference
	- Designed for future RAG, agents, and DB support

---

## Roadmap & Extensibility

- Add RAG (file indexing/search)
- Add agent workflows
- Add persistent storage (PostgreSQL)
- Dockerize for easy deployment

---

## Resources

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)

---

For questions or contributions, see the subproject READMEs or contact the dev team.
