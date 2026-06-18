# AI Chat App — a learning project

A full-stack AI chat application built to learn **Python / FastAPI / OpenAI / Docker**, coming
from a Laravel + React + Postgres background.

```
Browser ──HTTP/SSE──> FastAPI (uvicorn) ──> OpenAI API
                           │
                           └──> PostgreSQL (conversations, messages)
```

## Stack
- **Frontend:** React (Vite + TypeScript)
- **Backend:** FastAPI (Python 3.12), async SQLAlchemy, Alembic
- **DB:** PostgreSQL
- **LLM:** OpenAI API (`openai` SDK), default model `gpt-4o-mini`
- **Tooling:** `uv` (Python deps), `ruff` (lint/format), Docker (final phase)

## Quick start (local dev)

```bash
# 1. Backend
cd backend
cp .env.example .env          # fill in OPENAI_API_KEY + DATABASE_URL
uv sync                        # install deps into .venv
uv run alembic upgrade head    # create tables
uv run uvicorn app.main:app --reload   # http://localhost:8000/docs

# 2. Frontend (separate terminal)
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

## Learning roadmap

This repo is built in phases — see the plan file. Each phase ends in a runnable checkpoint.

- [x] Phase 0 — Repo + Claude Code setup
- [x] Phase 1 — Python env + language crash-course
- [x] Phase 2 — FastAPI hello chat
- [x] Phase 3 — Pydantic schemas
- [x] Phase 4 — PostgreSQL + SQLAlchemy + Alembic
- [x] Phase 5 — OpenAI integration
- [x] Phase 6 — Chat endpoints + SSE streaming
- [x] Phase 7 — React frontend
- [x] Phase 8 — Hardening
- [x] Phase 9 — Dockerize

## Run with Docker (everything in one command)

```bash
docker compose up --build      # db + backend + frontend
# then open http://localhost:5173
docker compose down            # stop (add -v to wipe the DB volume)
```

## Laravel → Python cheat sheet

| Laravel / PHP | Python / FastAPI |
|---|---|
| composer + vendor/ | `uv` + `.venv/` |
| composer.json | `pyproject.toml` |
| Routes + Controllers | FastAPI path operations |
| Form Request validation | Pydantic models |
| Eloquent | SQLAlchemy |
| artisan migrate | Alembic |
| service container / DI | `Depends()` |
| .env + config() | `pydantic-settings` |
| artisan serve | `uvicorn` |

## My learning notes
> Keep your own notes here as you go — what clicked, what confused you.
