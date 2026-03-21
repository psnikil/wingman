# Wingman: Local LLM Chat App (Full Stack)

Wingman is a full stack, locally running agentic AI app that lets you chat with open-source LLMs (via Ollama) on your own machine. It integrates with any frontend, supports different agents, and is designed for privacy, extensibility, and developer friendliness.

---

## Features

- **Local LLM chat**: Interact with Llama3 or other models using Ollama
- **Modern UI**: Built with Next.js, TailwindCSS, and TypeScript
- **FastAPI backend**: Clean, modular Python backend
- **Agents**: Supports multiple agents with different capabilities
- **Containerizable**: Future Docker support for easy deployment

---

## Project Structure

```
WingMan/
├── backend/    # FastAPI app (Python, Ollama integration)
├── TUI/   # Terminal UI app (Python, Rich)
└── README.md   # This file (global docs)
```

See each subfolder's README for detailed docs.

---

## Quick Start

### 1. Prerequisites

- **Python 3.10+** (for backend)
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
source .venv/bin/activate

uv sync
```

#### Run the backend server
```sh
uvicorn app.main:app --reload
# API at http://localhost:8000
```


---

## Main Requirements

- **Ollama**: For running LLMs locally ([installation guide](https://ollama.com/))
- **Python 3.10+**: Backend (FastAPI, Pydantic, etc.)


---

## High-Level Architecture


- **Backend**: FastAPI app (Python)
	- Handles chat, session, and LLM requests
	- Integrates with Ollama,langchain for LLM inference and agentic systems
	- Designed for easy addition of agents,tools and building dynamic agentic workflows

---

## Roadmap & Extensibility

- TODO

---

## Resources

- [Backend README](./backend/README.md)

---

For questions or contributions, see the subproject READMEs or contact the dev team.
